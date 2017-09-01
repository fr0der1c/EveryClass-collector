SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `ec_classes_16_17_2`
-- ----------------------------
DROP TABLE IF EXISTS `ec_classes_16_17_2`;
CREATE TABLE `ec_classes_16_17_2` (
  `clsname` text,
  `day` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `teacher` text,
  `duration` text,
  `week` text,
  `location` text,
  `students` text,
  `id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Table structure for `ec_classes_17_18_1`
-- ----------------------------
DROP TABLE IF EXISTS `ec_classes_17_18_1`;
CREATE TABLE `ec_classes_17_18_1` (
  `clsname` text,
  `day` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `teacher` text,
  `duration` text,
  `week` text,
  `location` text,
  `students` text,
  `id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Table structure for `ec_students`
-- ----------------------------
DROP TABLE IF EXISTS `ec_students`;
CREATE TABLE `ec_students` (
  `xh` varchar(40) NOT NULL,
  `semesters` text,
  `xs0101id` varchar(40) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`xh`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Table structure for `ec_students_16_17_2`
-- ----------------------------
DROP TABLE IF EXISTS `ec_students_16_17_2`;
CREATE TABLE `ec_students_16_17_2` (
  `xh` varchar(40) NOT NULL,
  `classes` longtext,
  PRIMARY KEY (`xh`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Table structure for `ec_students_17_18_1`
-- ----------------------------
DROP TABLE IF EXISTS `ec_students_17_18_1`;
CREATE TABLE `ec_students_17_18_1` (
  `xh` varchar(40) NOT NULL,
  `classes` longtext,
  PRIMARY KEY (`xh`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50719
 Source Host           : localhost
 Source Database       : everyclass

 Target Server Type    : MySQL
 Target Server Version : 50719
 File Encoding         : utf-8

 Date: 09/01/2017 16:18:53 PM
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `ec_stu_id_prefix`
-- ----------------------------
DROP TABLE IF EXISTS `ec_stu_id_prefix`;
CREATE TABLE `ec_stu_id_prefix` (
  `prefix` varchar(10) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`prefix`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Records of `ec_stu_id_prefix`
-- ----------------------------
BEGIN;
INSERT INTO `ec_stu_id_prefix` VALUES ('0101', '地质'), ('0105', '测绘'), ('0106', '地信'), ('0107', '遥感'), ('0108', '地勘'), ('0109', '工程试验班(地勘)'), ('0110', '地物'), ('0201', '采矿'), ('0202', '城地'), ('0203', '安全'), ('0204', '采矿'), ('0301', '矿物'), ('0302', '无机'), ('0303', '生工'), ('0401', '测绘'), ('0402', '生医'), ('0501', '冶金'), ('0502', '环境'), ('0506', '能器'), ('0603', '材料'), ('0701', '粉体'), ('0702', '材化'), ('0707', '高分子'), ('0801', '机械;材料成型'), ('0803', '微电子'), ('0815', '车辆'), ('0901', '自动化'), ('0902', '计算机'), ('0903', '电信'), ('0904', '测控'), ('0905', '通信'), ('0906', '信安'), ('0908', '电气'), ('0918', '智能'), ('0919', '物联网'), ('0921', '大数据'), ('1004', '新能源'), ('1006', '能动'), ('1007', '建环'), ('1101', '交运'), ('1103', '物流'), ('1109', '交设'), ('1201', '土木'), ('1202', '工管'), ('1203', '铁道'), ('1205', '工力'), ('1207', '消防'), ('1301', '应数'), ('1302', '信科'), ('1303', '统计'), ('1401', '应物;物理科学'), ('1402', '电科;物理科学'), ('1406', '光电;物理科学'), ('1501', '化工'), ('1502', '应化'), ('1503', '制药'), ('1601', '工商'), ('1602', '信管'), ('1603', '会计'), ('1604', '财务'), ('1605', '金融'), ('1606', '国贸'), ('1607', '电商'), ('1609', '营销'), ('1616', '工商(高水平)'), ('1701', '中文'), ('1704', '广电'), ('1705', '出版'), ('1801', '英语'), ('1903', '音乐'), ('1906', '视传'), ('1909', '城规'), ('1910', '建筑'), ('1911', '环设'), ('1912', '产设'), ('1914', '舞蹈'), ('2001', '法学'), ('2102', '思政'), ('2201', '临床（五年）'), ('2203', '精神'), ('2204', '临床（八年）'), ('2205', '麻醉'), ('2210', '生信'), ('2212', '检验'), ('2301', '法医'), ('2303', '基础医学'), ('2401', '药学'), ('2501', '护理'), ('2601', '预防'), ('2701', '口腔（五年）'), ('2703', '口腔（5 3）'), ('2801', '生科'), ('3901', '软件'), ('3903', '软件'), ('4201', '探控'), ('4205', '航天'), ('4301', '社会'), ('4302', '行政'), ('4304', '劳保'), ('6601', '运训');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
