-- ============================================
-- レシピ管理アプリ - テストデータ投入スクリプト
-- リファクタリング版
-- Docker MySQL初期化用
-- ============================================

-- ============================================
-- 1. マスターデータ投入
-- ============================================
-- 1-1. ソースタイプマスタデータ
INSERT INTO source_types (code, name, description, is_active) VALUES
('web', 'ウェブサイト', 'インターネット上のレシピサイトからの情報', TRUE),
('book', '書籍', '料理本や雑誌からのレシピ', TRUE),
('original', 'オリジナル', '自分で考案したオリジナルレシピ', TRUE);

-- 1-2. 写真タイプマスタデータ
INSERT INTO photo_types (code, name, description, is_reference, is_active) VALUES
('scraped', 'スクレイピング', 'ウェブサイトから取得した写真', TRUE, TRUE),
('book', '書籍', '本や雑誌からの写真', TRUE, TRUE),
('my_photo', '自分の写真', '実際に作った時の写真', FALSE, TRUE);

-- 1-3. カテゴリデータ
INSERT INTO categories (name, color) VALUES
('和食', '#FF6B6B'),
('洋食', '#4ECDC4'),
('中華', '#45B7D1'),
('メイン料理', '#FFB347'),
('副菜', '#98FB98'),
('デザート', '#F0E68C'),
('スープ', '#87CEEB'),
('サラダ', '#90EE90'),
('パン・パスタ', '#DEB887'),
('お弁当', '#FFB6C1'),
('時短料理', '#20B2AA');

-- 1-4. タグデータ
INSERT INTO tags (name) VALUES
('簡単'),
('時短'),
('ヘルシー'),
('節約'),
('作り置き'),
('お弁当'),
('辛い'),
('甘い'),
('さっぱり'),
('こってり'),
('冷凍保存可');

-- ============================================
-- 2. レシピデータ投入
-- ============================================
INSERT INTO recipes (title, description, cook_time, servings, source_type_id, source_url, rating) VALUES
('鶏の唐揚げ', '外はサクサク、中はジューシーな定番唐揚げ', 30, 4, 1, 'https://cookpad.com/recipe/sample1', 5),
('ハンバーグ', 'ふわふわジューシーなハンバーグ', 45, 4, 1, 'https://cookpad.com/recipe/sample2', 4);

INSERT INTO recipes (title, description, cook_time, servings, source_type_id, source_book_title, source_page, rating) VALUES
('肉じゃが', '母の味を再現した懐かしい肉じゃが', 40, 4, 2, '家庭料理の基本', 45, 5);
-- ============================================
-- 3. 材料データ投入
-- ============================================
-- 鶏の唐揚げ（recipe_id: 1）
INSERT INTO ingredients (recipe_id, name, quantity, unit, sort_order) VALUES
(1, '鶏もも肉', '500', 'g', 1),
(1, '醤油', '大さじ2', '', 2),
(1, '酒', '大さじ1', '', 3),
(1, '生姜（すりおろし）', '小さじ1', '', 4),
(1, 'にんにく（すりおろし）', '小さじ1', '', 5),
(1, '片栗粉', '適量', '', 6),
(1, '揚げ油', '適量', '', 7);

-- ハンバーグ（recipe_id: 2）
INSERT INTO ingredients (recipe_id, name, quantity, unit, sort_order) VALUES
(2, '合いびき肉', '300', 'g', 1),
(2, '玉ねぎ', '1', '個', 2),
(2, 'パン粉', '1/2', 'カップ', 3),
(2, '牛乳', '大さじ3', '', 4),
(2, '卵', '1', '個', 5),
(2, '塩', '小さじ1/2', '', 6),
(2, 'こしょう', '少々', '', 7),
(2, 'サラダ油', '大さじ1', '', 8);

-- チャーハン（recipe_id: 3）
INSERT INTO ingredients (recipe_id, name, quantity, unit, sort_order) VALUES
(3, 'ご飯', '2', '膳分', 1),
(3, '卵', '2', '個', 2),
(3, 'ハム', '2', '枚', 3),
(3, '長ねぎ', '1/2', '本', 4),
(3, '醤油', '大さじ1', '', 5),
(3, '塩', '少々', '', 6),
(3, 'ごま油', '大さじ1', '', 7);
-- ============================================
-- 4. 手順データ投入
-- ============================================
-- 鶏の唐揚げ（recipe_id: 1）
INSERT INTO steps (recipe_id, step_number, instruction, time_estimate) VALUES
(1, 1, '鶏もも肉を一口大に切り、醤油、酒、生姜、にんにくで下味をつけ30分漬け込む', 35),
(1, 2, '片栗粉をまぶして、170度の油で4-5分揚げる', 10),
(1, 3, '一度取り出し、油の温度を180度に上げて1-2分二度揚げする', 5);

-- ハンバーグ（recipe_id: 2）
INSERT INTO steps (recipe_id, step_number, instruction, time_estimate) VALUES
(2, 1, '玉ねぎをみじん切りにして炒め、冷ましておく', 10),
(2, 2, 'パン粉を牛乳に浸しておく', 5),
(2, 3, 'ボウルにひき肉、炒めた玉ねぎ、パン粉、卵、塩こしょうを入れてよく混ぜる', 5),
(2, 4, '4等分して楕円形に成形し、中央を少しくぼませる', 5),
(2, 5, 'フライパンに油を熱し、中火で両面3分ずつ焼き、蓋をして弱火で10分蒸し焼きにする', 20);

-- チャーハン（recipe_id: 3）
INSERT INTO steps (recipe_id, step_number, instruction, time_estimate) VALUES
(3, 1, '卵を溶き、ハムと長ねぎを細かく切る', 5),
(3, 2, '強火で熱したフライパンに油を入れ、溶き卵を入れてすぐにご飯を加える', 3),
(3, 3, 'ご飯と卵をよく混ぜ合わせ、パラパラになるまで炒める', 5),
(3, 4, 'ハムと長ねぎを加えて炒め、醤油と塩で味付けし、ごま油で仕上げる', 2);
-- ============================================
-- 5. レシピ-カテゴリ関連データ
-- ============================================
INSERT INTO recipe_categories (recipe_id, category_id) VALUES
(1, 1), -- チキンカレー - メイン料理
(1, 4), -- チキンカレー - 簡単料理
(2, 1), -- 肉じゃが - 和食
(3, 2), -- ペペロンチーノ - 洋食
(3, 5); -- ペペロンチーノ - 時短料理

-- ============================================
-- 6. レシピ-タグ関連データ
-- ============================================
INSERT INTO recipe_tags (recipe_id, tag_id) VALUES
(1, 1), -- チキンカレー - 簡単
(1, 3), -- チキンカレー - 子供向け
(2, 1), -- 肉じゃが - 簡単
(2, 5), -- 肉じゃが - 作り置き
(3, 2), -- ペペロンチーノ - 時短
(3, 3); -- ペペロンチーノ - フライパン一つ

-- ============================================
-- 7. サンプル調理記録
-- ============================================
INSERT INTO cooking_records (recipe_id, cooking_date, actual_servings, actual_cook_time, rating, cooking_memo, difficulty_rating, estimated_cost, occasion) VALUES
(1, '2025-06-10', 4, 35, 5, '家族に大好評！二度揚げがポイント', 3, 800.00, '夕食'),
(2, '2025-06-12', 3, 50, 4, '少し焼きすぎた。次回は火加減に注意', 4, 600.00, '夕食'),
(3, '2025-06-15', 2, 12, 4, '簡単で美味しい。一人ランチにも最適', 2, 300.00, '昼食');
-- ============================================
-- 8. サンプル写真データ
-- ============================================
INSERT INTO recipe_photos (recipe_id, photo_url, photo_type_id, is_primary, sort_order, alt_text) VALUES
(1, 'https://example.com/images/chicken-curry-ref.jpg', 1, TRUE, 1, 'チキンカレーの参考写真'),
(1, '/uploads/my-chicken-curry-2024-12-01.jpg', 3, FALSE, 2, '実際に作ったチキンカレー'),
(2, '/uploads/my-nikujaga-2024-12-02.jpg', 3, FALSE, 1, '実際に作った肉じゃが'),
(3, '/uploads/my-peperoncino-2024-12-03.jpg', 3, FALSE, 1, '実際に作ったペペロンチーノ');

-- ============================================
-- 9. データ投入完了確認
-- ============================================

-- 投入データの統計情報
-- データ確認用クエリ
-- 登録されたレシピ一覧を確認
SELECT 
    r.title,
    st.name AS source_type,
    r.cook_time,
    r.rating,
    r.cooking_date
FROM recipes r
JOIN source_types st ON r.source_type_id = st.id
ORDER BY r.id;

-- カテゴリ別レシピ数を確認
SELECT 
    c.name AS category_name,
    COUNT(rc.recipe_id) AS recipe_count
FROM categories c
LEFT JOIN recipe_categories rc ON c.id = rc.category_id
GROUP BY c.id, c.name
ORDER BY recipe_count DESC;

-- タグ別レシピ数を確認
SELECT 
    t.name AS tag_name,
    COUNT(rt.recipe_id) AS recipe_count
FROM tags t
LEFT JOIN recipe_tags rt ON t.id = rt.tag_id
GROUP BY t.id, t.name
ORDER BY recipe_count DESC;