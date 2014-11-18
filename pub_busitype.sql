# Host: 127.0.0.1  (Version: 5.6.21-log)
# Date: 2014-10-24 13:56:26
# Generator: MySQL-Front 5.3  (Build 4.175)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "pub_busitype"
#

DROP TABLE IF EXISTS `pub_busitype`;
CREATE TABLE `pub_busitype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


 Data for table "pub_busitype"


INSERT INTO `pub_busitype` VALUES (1,'短信',1,'2014-10-22 15:00:00'),(2,'彩信',1,'2014-10-22 15:00:00'),(3,'WAP',1,'2014-10-22 15:00:00');
