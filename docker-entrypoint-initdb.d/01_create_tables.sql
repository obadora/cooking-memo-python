-- レシピアプリ テーブル作成スクリプト
-- Docker MySQL初期化用
-- 注意: MYSQL_DATABASEで指定したデータベースが自動選択されるため、USE文は不要

-- ソースタイプマスタテーブル
CREATE TABLE source_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE COMMENT 'web, book, magazine, original',
    name VARCHAR(50) NOT NULL COMMENT 'ウェブサイト, 書籍, 雑誌, オリジナル',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source_types_code (code),
    INDEX idx_source_types_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='ソースタイプマスタテーブル';

-- 写真タイプマスタテーブル
CREATE TABLE photo_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE COMMENT 'scraped, book, my_photo',
    name VARCHAR(50) NOT NULL COMMENT 'スクレイピング, 書籍, 自分の写真',
    description TEXT,
    is_reference BOOLEAN DEFAULT FALSE COMMENT '参考写真かどうか（上部表示用）',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_photo_types_code (code),
    INDEX idx_photo_types_reference (is_reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='写真タイプマスタテーブル';

-- カテゴリテーブル
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#CCCCCC' COMMENT '色コード',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='カテゴリテーブル';

-- タグテーブル
CREATE TABLE tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tags_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='タグテーブル';

-- メインのレシピテーブル
CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cook_time INT COMMENT '調理時間（分）',
    servings INT COMMENT '人数分',
    source_type_id INT NOT NULL,
    source_url VARCHAR(500) COMMENT 'webの場合のみ',
    source_book_title VARCHAR(255) COMMENT '本の場合',
    source_page INT COMMENT '本のページ番号',
    manual_identifier VARCHAR(100) COMMENT '手動設定の識別子',
    cooking_date DATE COMMENT 'カレンダーで選択した料理日',
    cooking_memo TEXT COMMENT 'その日の料理メモ（味の感想、改良点など）',
    rating TINYINT CHECK (rating >= 1 AND rating <= 5) COMMENT '5段階評価',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (source_type_id) REFERENCES source_types(id),
    INDEX idx_recipes_source_type (source_type_id),
    INDEX idx_recipes_cooking_date (cooking_date),
    INDEX idx_recipes_rating (rating),
    INDEX idx_recipes_title (title),
    FULLTEXT idx_recipes_search (title, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='メインのレシピテーブル';

-- 実際に作った記録テーブル
CREATE TABLE cooking_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL COMMENT 'レシピID',
    cooking_date DATE NOT NULL COMMENT '調理実施日',
    actual_servings INT COMMENT '実際の人数分',
    actual_cook_time INT COMMENT '実際の調理時間（分）',
    rating INT CHECK (rating >= 1 AND rating <= 5) COMMENT '5段階評価',
    cooking_memo TEXT COMMENT '調理メモ',
    difficulty_rating INT CHECK (difficulty_rating >= 1 AND difficulty_rating <= 5) COMMENT '難易度評価',
    estimated_cost DECIMAL(10,2) COMMENT '推定コスト',
    occasion VARCHAR(100) COMMENT '機会・シーン',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
    
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_recipe_cooking_date (recipe_id, cooking_date),
    INDEX idx_cooking_date (cooking_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci, COMMENT='調理実施記録';

-- 写真管理テーブル
CREATE TABLE recipe_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    photo_url VARCHAR(500) NOT NULL,
    photo_type_id INT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE COMMENT 'メイン表示用の写真かどうか（参考写真のみ）',
    sort_order INT DEFAULT 0 COMMENT '表示順序',
    alt_text VARCHAR(255) COMMENT '代替テキスト',
    file_size INT COMMENT 'ファイルサイズ（バイト）',
    width INT COMMENT '画像幅',
    height INT COMMENT '画像高さ',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (photo_type_id) REFERENCES photo_types(id),
    INDEX idx_recipe_photos_recipe_id (recipe_id),
    INDEX idx_recipe_photos_primary (recipe_id, is_primary),
    INDEX idx_recipe_photos_type (photo_type_id),
    INDEX idx_recipe_photos_sort (recipe_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='写真管理テーブル';

-- 材料テーブル
CREATE TABLE ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    quantity VARCHAR(100) COMMENT '分量ではあるが、現時点では1枚(250g)みたいにしている',
    unit VARCHAR(30) COMMENT '現時点ではつかってない',
    sort_order INT DEFAULT 0,
    notes TEXT COMMENT '材料に関する補足',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_ingredients_recipe_id (recipe_id),
    INDEX idx_ingredients_sort (recipe_id, sort_order),
    INDEX idx_ingredients_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='材料テーブル';

-- 手順テーブル
CREATE TABLE steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    step_number INT NOT NULL,
    instruction TEXT NOT NULL,
    time_estimate INT COMMENT '分単位',
    temperature INT COMMENT '温度（℃）',
    notes TEXT COMMENT '手順に関する補足',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_steps_recipe_id (recipe_id),
    UNIQUE KEY unique_recipe_step (recipe_id, step_number),
    FULLTEXT idx_steps_instruction (instruction)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='手順テーブル';

-- レシピ-カテゴリ関連テーブル
CREATE TABLE recipe_categories (
    recipe_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (recipe_id, category_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_recipe_categories_recipe (recipe_id),
    INDEX idx_recipe_categories_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='レシピ-カテゴリ関連テーブル';

-- レシピ-タグ関連テーブル
CREATE TABLE recipe_tags (
    recipe_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    INDEX idx_recipe_tags_recipe (recipe_id),
    INDEX idx_recipe_tags_tag (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='レシピ-タグ関連テーブル';

-- =============================================
-- テーブル作成確認用クエリ
-- =============================================

-- 作成されたテーブル一覧を確認
SHOW TABLES;

-- テーブルサイズとエンジン情報を確認
SELECT 
    TABLE_NAME,
    ENGINE,
    TABLE_ROWS,
    DATA_LENGTH,
    INDEX_LENGTH,
    TABLE_COLLATION
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME;