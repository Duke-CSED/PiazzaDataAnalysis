BEGIN TRANSACTION;
-- Primary tables shared across data sources

DROP TABLE IF EXISTS semester;
CREATE TABLE semester(
    id INTEGER NOT NULL,
    sName TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_semester_id ON semester (id);

INSERT INTO semester (id, sName)
VALUES
    (1, 'fa14'),
    (2, 'sp15'),
    (3, 'fa15'),
    (4, 'sp16'),
    (5, 'fa16'),
    (6, 'sp17'),
    (7, 'fa17'),
    (8, 'sp18'),
    (9, 'fa18'),
    (10, 'sp19');


DROP TABLE IF EXISTS dataSrc;
CREATE TABLE dataSrc(
    id INTEGER PRIMARY KEY ASC,
    dsName TEXT NOT NULL,
    dsDesc TEXT NOT NULL
);


DROP TABLE IF EXISTS student;
CREATE TABLE student(
    id INTEGER PRIMARY KEY ASC,
    semStart REFERENCES semester(id),
    semEnd REFERENCES semester(id)
);


DROP TABLE IF EXISTS student_dataSrc;
CREATE TABLE student_dataSrc(
    stuId REFERENCES student(id),
    dsId REFERENCES dataSrc(id),
    anonId TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_student_dataSrc_dsId_anonId ON student_dataSrc (dsId,anonId);

DROP VIEW IF EXISTS student_dataSrcName;
CREATE VIEW student_dataSrcName AS
SELECT sDS.stuId as stuId, sDS.anonId AS anonId,
    ds.id AS dsId, ds.dsName as dsName
FROM student_dataSrc AS sDS
    JOIN dataSrc AS ds
        ON ds.id = sDS.dsId
;


DROP TABLE IF EXISTS studentActivityType;
CREATE TABLE studentActivityType(
    id INTEGER PRIMARY KEY ASC,
    satName TXT NOT NULL,
    satDesc TXT NOT NULL
);

INSERT INTO studentActivityType (satName, satDesc)
VALUES
    ('exam', 'Exam for the course'),
    ('code-assignment', 'A coding assignment for the course'),
    ('apt', 'A coding task that is on the level of a single function and therefore smaller than a code-assignment');


DROP TABLE IF EXISTS studentActivity;
CREATE TABLE studentActivity(
    id INTEGER PRIMARY KEY ASC,
    saName TXT NOT NULL,
    saDesc TXT NOT NULL,
    semId REFERENCES semester(id),
    typeId REFERENCES studentActivityType(id)
);


-- Tables tracking data processing
DROP TABLE IF EXISTS dataProcessed;
CREATE TABLE dataProcessed(
    created DATETIME,
    modified DATETIME,
    dsId REFERENCES dataSrc(id),
    semId REFERENCES semester(id)
);

CREATE INDEX IF NOT EXISTS idx_dataProcessed_dsId ON dataProcessed (dsId);
CREATE INDEX IF NOT EXISTS idx_dataProcessed_semId ON dataProcessed (semId);
CREATE INDEX IF NOT EXISTS idx_dataProcessed_dsId_semId ON dataProcessed (dsId, semId);


END TRANSACTION;


