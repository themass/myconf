-- MySQL dump 10.13  Distrib 5.6.24, for Win64 (x86_64)
--
-- Host: localhost    Database: vpn
-- ------------------------------------------------------
-- Server version	5.6.26-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `iwanna`
--

DROP TABLE IF EXISTS `iwanna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `iwanna` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `content` varchar(150) COLLATE utf8_bin DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `create_time` date DEFAULT NULL,
  `like_users` varchar(2000) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=263 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `iwanna`
--

LOCK TABLES `iwanna` WRITE;
/*!40000 ALTER TABLE `iwanna` DISABLE KEYS */;
INSERT INTO `iwanna` VALUES (165,'22','22',1,NULL,'33qq'),(166,'22','22',5,NULL,'33qq'),(167,'22','22',3,NULL,'33qq'),(168,'22','22',4,NULL,'33qq'),(169,'22','22',5,NULL,'33qq'),(170,'22','22',6,NULL,'33qq'),(171,'22','22',7,NULL,'33qq'),(172,'22','22',8,NULL,'33qq'),(173,'22','22',9,NULL,'33qq'),(174,'22','22',10,NULL,'33qq'),(175,'22','22',11,NULL,'33qq'),(176,'22','22',12,NULL,'33qq'),(177,'22','22',13,NULL,'33qq'),(178,'22','22',14,NULL,'33qq'),(179,'22','22',15,NULL,'33qq'),(180,'22','22',16,NULL,'33qq'),(181,'22','22',17,NULL,'33qq'),(182,'22','22',18,NULL,'33qq'),(183,'22','22',19,NULL,'33qq'),(184,'22','22',20,NULL,'33qq'),(185,'22','22',21,NULL,'33qq'),(186,'22','22',22,NULL,'33qq'),(187,'22','22',23,NULL,'33qq'),(188,'22','22',24,NULL,'33qq'),(189,'22','22',25,NULL,'33qq'),(190,'22','22',26,NULL,'33qq'),(191,'22','22',27,NULL,'33qq'),(192,'22','22',28,NULL,'33qq'),(193,'22','22',29,NULL,'33qq'),(194,'22','22',30,NULL,'33qq'),(195,'22','22',31,NULL,'33qq'),(196,'22','22',32,NULL,'33qq'),(197,'22','22',33,NULL,'33qq'),(198,'22','22',34,NULL,'33qq'),(199,'22','22',35,NULL,'33qq'),(200,'22','22',36,NULL,'33qq'),(201,'22','22',37,NULL,'33qq'),(202,'22','22',38,NULL,'33qq'),(203,'22','22',39,NULL,'33qq'),(204,'22','22',40,NULL,'33qq'),(205,'22','22',41,NULL,'33qq'),(206,'22','22',42,NULL,'33qq'),(207,'22','22',43,NULL,'33qq'),(208,'22','22',44,NULL,'33qq'),(209,'22','22',45,NULL,'33qq'),(210,'22','22',46,NULL,'33qq'),(211,'22','22',47,NULL,'33qq'),(212,'22','22',48,NULL,'33qq'),(213,'22','22',49,NULL,'33qq'),(214,'22','22',50,NULL,'33qq'),(215,'22','22',51,NULL,'33qq'),(216,'22','22',52,NULL,'33qq'),(217,'22','22',53,NULL,'33qq'),(218,'22','22',54,NULL,'33qq'),(219,'22','22',55,NULL,'33qq'),(220,'22','22',56,NULL,'33qq'),(221,'22','22',57,NULL,'33qq'),(222,'22','22',58,NULL,'33qq'),(223,'22','22',59,NULL,'33qq'),(224,'22','22',60,NULL,'33qq'),(225,'22','22',61,NULL,'33qq'),(226,'22','22',62,NULL,'33qq'),(227,'22','22',63,NULL,'33qq'),(228,'22','22',64,NULL,'33qq'),(229,'22','22',65,NULL,'33qq'),(230,'22','22',66,NULL,'33qq'),(231,'22','22',67,NULL,'33qq'),(232,'22','22',68,NULL,'33qq'),(233,'22','22',69,NULL,'33qq'),(234,'22','22',78,NULL,'33qq'),(235,'22','22',71,NULL,'33qq'),(236,'22','22',72,NULL,'33qq'),(237,'22','22',83,NULL,'33qq'),(238,'22','22',75,NULL,'33qq'),(239,'22','22',75,NULL,'33qq'),(240,'22','22',76,NULL,'33qq'),(241,'22','22',81,NULL,'33qq'),(242,'22','22',79,NULL,'33qq'),(243,'22','22',79,NULL,'33qq'),(244,'22','22',80,NULL,'33qq'),(245,'22','22',81,NULL,'33qq'),(246,'22','22',82,NULL,'33qq'),(247,'22','22',83,NULL,'33qq'),(248,'22','22',84,NULL,'33qq'),(249,'22','22',85,NULL,'33qq'),(250,'22','22',86,NULL,'33qq'),(251,'22','22',87,NULL,'33qq'),(252,'22','22',88,NULL,'33qq'),(253,'22','22',89,NULL,'33qq'),(254,'22','22',90,NULL,'33qq'),(255,'22','22',91,NULL,'33qq'),(256,'22','22',92,NULL,'33qq'),(257,'22','22',93,NULL,'33qq'),(258,'22','22',94,NULL,'33qq'),(259,'qqq','热腾腾甜甜',0,'2016-09-08','8>'),(260,'qqq','嘎嘎嘎嘎嘎嘎嘎嘎广告的时候被子弹性别老师父亲们呢！滚滚滚红尘情歌曲线程度假期待客厅长期待客厅',0,'2016-09-08','8>'),(261,'qqq','哈哈哈',0,'2016-09-08','8>'),(262,'qqq','哈哈哈哈好',0,'2016-09-08','8>');
/*!40000 ALTER TABLE `iwanna` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-12-14 21:15:14
