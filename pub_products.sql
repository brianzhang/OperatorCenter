# Host: 127.0.0.1  (Version: 5.6.21-log)
# Date: 2014-10-24 13:58:10
# Generator: MySQL-Front 5.3  (Build 4.175)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "pub_products"
#

DROP TABLE IF EXISTS `pub_products`;
CREATE TABLE `pub_products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proname` varchar(50) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `content` varchar(100) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

#
# Data for table "pub_products"
#

INSERT INTO `pub_products` VALUES (1,'MTK',1,'彩信增值通道','2014-10-22 10:00:00'),(2,'网游',1,'网游扣费通道','2014-10-22 10:00:00'),(3,'包月',1,'包月服务','2014-10-22 10:00:00'),(4,'IVR',1,'包月服务','2014-10-22 10:00:00');
