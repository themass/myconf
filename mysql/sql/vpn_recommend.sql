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
-- Table structure for table `recommend`
--

DROP TABLE IF EXISTS `recommend`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recommend` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(45) COLLATE utf8_bin NOT NULL,
  `actionUrl` varchar(45) COLLATE utf8_bin NOT NULL,
  `img` varchar(100) COLLATE utf8_bin DEFAULT NULL,
  `desc` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `sort` int(11) DEFAULT NULL,
  `enable` int(11) DEFAULT '1',
  `color` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `rate` float DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recommend`
--

LOCK TABLES `recommend` WRITE;
/*!40000 ALTER TABLE `recommend` DISABLE KEYS */;
INSERT INTO `recommend` VALUES (1,'Google','https://www.google.com/','http://static2.mobile.ljcdn.com/recommend/google.jpg?11',NULL,NULL,1,'#dedfe4',0.6),(2,'YouTube','https://m.youtube.com/','http://static2.mobile.ljcdn.com/recommend/youtube.jpg?11',NULL,NULL,1,'#cfcfcf',1),(3,'Wikipedia','https://en.wikipedia.org/wiki/Main_Page','http://static2.mobile.ljcdn.com/recommend/wiki.jpg?11',NULL,NULL,1,'#f2f2f2',0.63),(4,'Facebook','https://m.facebook.com/','http://static2.mobile.ljcdn.com/recommend/facebook.jpg?11',NULL,NULL,1,'#355393',1),(5,'Twitter','https://mobile.twitter.com/','http://static2.mobile.ljcdn.com/recommend/twtter.jpg?11',NULL,NULL,1,'#2380c5',1),(6,'CNN','http://edition.cnn.com/','http://static2.mobile.ljcdn.com/recommend/cnn.jpg?11',NULL,NULL,1,'#f70009',1),(7,' Tumblr','http://mashable.com/category/tumblr/','http://static2.mobile.ljcdn.com/recommend/tumblr.jpg?11',NULL,NULL,1,'#33536c',0.82),(8,'DailyMail','http://www.dailymail.co.uk/home/index.html','http://static2.mobile.ljcdn.com/recommend/dailymail.jpg?11',NULL,NULL,1,'#dfdfdf',1),(9,'BuzzFeed','https://www.buzzfeed.com/','http://static2.mobile.ljcdn.com/recommend/buzzfeed.jpg?11',NULL,NULL,1,'#d1140e',1),(10,'BoredPanda','http://www.boredpanda.com/','http://static2.mobile.ljcdn.com/recommend/boredpanda.jpg?11',NULL,NULL,1,'',1),(11,'Amazon','http://www.amazon.com/','http://static2.mobile.ljcdn.com/recommend/amazon.jpg?11',NULL,NULL,1,'#1165a5',1);
/*!40000 ALTER TABLE `recommend` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-12-14 21:15:15
