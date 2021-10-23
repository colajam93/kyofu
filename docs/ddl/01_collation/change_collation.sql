alter table library
    modify `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
    modify `base_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL
;

alter table song
    modify `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL
;
