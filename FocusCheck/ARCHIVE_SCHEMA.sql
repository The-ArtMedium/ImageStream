-- This table connects your photography 'eye' with your data 'brain'
CREATE TABLE ImageArchive (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    folder_path TEXT,
    focus_score FLOAT,          -- The Laplacian Variance we calculated
    iso INTEGER,                -- Helps you track the 'Noise Trap'
    shutter_speed TEXT,         -- Helps analyze motion blur
    aperture FLOAT,             -- Analyze depth of field vs focus score
    lens_model TEXT,
    date_captured DATETIME,
    classification TEXT         -- 'Keeper', 'Review', or 'Trash' based on score
);

-- Example Query: Find my top 10 sharpest 'Landscape' shots
SELECT filename, focus_score 
FROM ImageArchive 
WHERE focus_score > 800 
ORDER BY focus_score DESC 
LIMIT 10;
