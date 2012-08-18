-- CREATE TABLE "exercises_exercisecategory" (
--     "id" integer NOT NULL PRIMARY KEY,
--     "name" varchar(100) NOT NULL
-- );
INSERT INTO "exercises_exercisecategory" VALUES(1,'Arme');
INSERT INTO "exercises_exercisecategory" VALUES(2,'Beine');
INSERT INTO "exercises_exercisecategory" VALUES(3,'Bauch');

-- CREATE TABLE "exercises_exercise" (
--     "id" integer NOT NULL PRIMARY KEY,
--     "category_id" integer NOT NULL REFERENCES "manager_exercisecategory" ("id"),
--     "name" varchar(200) NOT NULL
-- );
INSERT INTO "exercises_exercise" VALUES(1,1,'Trizeps Seildrücken');
INSERT INTO "exercises_exercise" VALUES(2,2,'Bizeps am Kabel');
INSERT INTO "exercises_exercise" VALUES(3,2,'Beinpresse');
INSERT INTO "exercises_exercise" VALUES(4,2,'Kniebeuge');
INSERT INTO "exercises_exercise" VALUES(5,3,'Crunches');
INSERT INTO "exercises_exercise" VALUES(6,1,'Curls');
INSERT INTO "exercises_exercise" VALUES(7,2,'Ausfallschritte');
