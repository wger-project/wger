-- CREATE TABLE "exercises_language" (
--     "id" integer NOT NULL PRIMARY KEY,
--     "short_name" varchar(2) NOT NULL,
--     "full_name" varchar(30) NOT NULL
-- )
INSERT INTO "exercises_language" VALUES(1,'de','Deutsch');
INSERT INTO "exercises_language" VALUES(2,'en','English');


-- CREATE TABLE "exercises_exercisecategory" (
--     "id" integer NOT NULL PRIMARY KEY,
--     "name" varchar(100) NOT NULL,
--     "language_id" integer NOT NULL REFERENCES "exercises_language" ("id")
-- )
INSERT INTO "exercises_exercisecategory" VALUES(1,'Arme',1);
INSERT INTO "exercises_exercisecategory" VALUES(2,'Beine',1);
INSERT INTO "exercises_exercisecategory" VALUES(3,'Rücken',1);
INSERT INTO "exercises_exercisecategory" VALUES(4,'Bauch',1);
INSERT INTO "exercises_exercisecategory" VALUES(5,'Schultern',1);
INSERT INTO "exercises_exercisecategory" VALUES(6,'Waden',1);
INSERT INTO "exercises_exercisecategory" VALUES(7,'Brust',1);



-- CREATE TABLE "exercises_exercise" (
--     "id" integer NOT NULL PRIMARY KEY,
--     "category_id" integer NOT NULL REFERENCES "exercises_exercisecategory" ("id"),
--     "description" varchar(2000) NOT NULL,
--     "name" varchar(200) NOT NULL UNIQUE
-- )

INSERT INTO "exercises_exercise" VALUES(1,1,'','Trizeps Seildrücken',1);
INSERT INTO "exercises_exercise" VALUES(2,1,'','Curls',1);
INSERT INTO "exercises_exercise" VALUES(3,1,'','Bizeps am Kabel',1);
INSERT INTO "exercises_exercise" VALUES(4,4,'','Crunches',1);
INSERT INTO "exercises_exercise" VALUES(5,2,'','Ausfallschritte im Gehen',1);
INSERT INTO "exercises_exercise" VALUES(6,2,'','Beinpresse',1);
INSERT INTO "exercises_exercise" VALUES(7,2,'','Kniebeuge',1);
INSERT INTO "exercises_exercise" VALUES(8,5,'','Shrugs',1);
INSERT INTO "exercises_exercise" VALUES(9,3,'','Kreuzheben',1);
INSERT INTO "exercises_exercise" VALUES(10,3,'','Frontziehen breit',1);
INSERT INTO "exercises_exercise" VALUES(11,3,'','Einarmiges rudern KH',1);
INSERT INTO "exercises_exercise" VALUES(12,3,'','Frontziehen eng',1);
INSERT INTO "exercises_exercise" VALUES(13,6,'','Wadenheben stehend',1);
INSERT INTO "exercises_exercise" VALUES(14,6,'','Wadenheben sitzend',1);
INSERT INTO "exercises_exercise" VALUES(15,7,'','Bankdrücken LH',1);
INSERT INTO "exercises_exercise" VALUES(16,7,'','Schrägbankdrücken KH',1);
INSERT INTO "exercises_exercise" VALUES(17,7,'','Negativ Bankdrücken',1);
INSERT INTO "exercises_exercise" VALUES(18,7,'','Fliegende KH Flachbank',1);
INSERT INTO "exercises_exercise" VALUES(19,5,'','Frontdrücken KH',1);
INSERT INTO "exercises_exercise" VALUES(20,5,'','Seitheben KH',1);
INSERT INTO "exercises_exercise" VALUES(21,5,'','Butterfly reverse',1);
INSERT INTO "exercises_exercise" VALUES(22,2,'','Beinbeuger liegend',1);
INSERT INTO "exercises_exercise" VALUES(23,6,'','Hackenschmidt',1);
INSERT INTO "exercises_exercise" VALUES(24,1,'','Bizeps LH-Curls',1);
INSERT INTO "exercises_exercise" VALUES(25,1,'','Frenchpress ß-Stange',1);
INSERT INTO "exercises_exercise" VALUES(26,1,'','Bizeps KH-Curls',1);
INSERT INTO "exercises_exercise" VALUES(27,1,'','Trizepsmaschine',1);
INSERT INTO "exercises_exercise" VALUES(28,1,'','KH an Scottmaschine',1);
INSERT INTO "exercises_exercise" VALUES(29,1,'','Dips',1);
INSERT INTO "exercises_exercise" VALUES(30,7,'','Butterfly',1);
INSERT INTO "exercises_exercise" VALUES(31,7,'','Umsetzen',1);
INSERT INTO "exercises_exercise" VALUES(32,4,'','Crunches an Negativbank',1);
INSERT INTO "exercises_exercise" VALUES(33,4,'','Crunches am Seil',1);
INSERT INTO "exercises_exercise" VALUES(34,4,'','Beinheben liegend',1);
INSERT INTO "exercises_exercise" VALUES(35,4,'','Beinheben aufrecht',1);
INSERT INTO "exercises_exercise" VALUES(36,3,'','Klimmzüge',1);
INSERT INTO "exercises_exercise" VALUES(37,3,'','Long-Pulley',1);
INSERT INTO "exercises_exercise" VALUES(38,1,'','Bankdrücken eng',1);
INSERT INTO "exercises_exercise" VALUES(39,2,'','Beinstrecker',1);
INSERT INTO "exercises_exercise" VALUES(40,7,'','Überzugmaschine',1);
INSERT INTO "exercises_exercise" VALUES(41,7,'','Schrägbankdrücken LH',1);
INSERT INTO "exercises_exercise" VALUES(42,5,'','Rudern aufgelegt',1);
INSERT INTO "exercises_exercise" VALUES(43,5,'','Nackenziehen',1);
INSERT INTO "exercises_exercise" VALUES(44,1,'','Bizeps Cursl mit ß-Stange ',1);
INSERT INTO "exercises_exercise" VALUES(45,1,'','Trizepsdrücken KH über Kopf',1);
INSERT INTO "exercises_exercise" VALUES(46,1,'','Hammercurls',1);
INSERT INTO "exercises_exercise" VALUES(47,5,'','Vorgebeugtes Seitheben',1);
INSERT INTO "exercises_exercise" VALUES(48,3,'','Klimmzüge an Maschine',1);
INSERT INTO "exercises_exercise" VALUES(49,3,'','MGM-Maschine',1);
INSERT INTO "exercises_exercise" VALUES(50,3,'','Good Mornings',1);
INSERT INTO "exercises_exercise" VALUES(51,4,'','Crunches an Maschine',1);
INSERT INTO "exercises_exercise" VALUES(52,7,'','Butterfly eng',1);
INSERT INTO "exercises_exercise" VALUES(53,5,'','Schultermaschine',1);
INSERT INTO "exercises_exercise" VALUES(54,2,'','Beinpresse eng',1);
INSERT INTO "exercises_exercise" VALUES(55,2,'','Ausfallschritte stehend',1);
INSERT INTO "exercises_exercise" VALUES(56,4,'','Crunches am Stuhl',1);
INSERT INTO "exercises_exercise" VALUES(57,4,'','Sit Ups',1);
INSERT INTO "exercises_exercise" VALUES(58,1,'','Frenchpress KH',1);
INSERT INTO "exercises_exercise" VALUES(59,3,'','Rudern vorgebeugt LH',1);
INSERT INTO "exercises_exercise" VALUES(60,3,'','Hyperextensions',1);
INSERT INTO "exercises_exercise" VALUES(61,3,'','Schrägbankdrücken MP',1);
INSERT INTO "exercises_exercise" VALUES(62,5,'','Rudern aufrecht ß-Stange',1);
INSERT INTO "exercises_exercise" VALUES(63,1,'','Trizeps Seildrücken mit Stange',1);
INSERT INTO "exercises_exercise" VALUES(64,2,'','Rumpfbeugen',1);
INSERT INTO "exercises_exercise" VALUES(65,5,'','Frontheben am Kabel',1);
INSERT INTO "exercises_exercise" VALUES(66,5,'','Schulterdrücken MP',1);
INSERT INTO "exercises_exercise" VALUES(67,5,'','Schulterheben MP',1);
INSERT INTO "exercises_exercise" VALUES(68,1,'','Dips zwischen 2 Bänke',1);
INSERT INTO "exercises_exercise" VALUES(69,2,'','Beinstrecker einbeinig',1);
INSERT INTO "exercises_exercise" VALUES(70,3,'','Rudern vorgebeugt LH reverse',1);
INSERT INTO "exercises_exercise" VALUES(71,7,'','Kabelcross',1);
INSERT INTO "exercises_exercise" VALUES(72,2,'','Beinbeuger stehend',1);
INSERT INTO "exercises_exercise" VALUES(73,7,'','Fliegende KH Schrägbank',1);
