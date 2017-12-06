CREATE DATABASE  IF NOT EXISTS `SMIStatus` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `SMIStatus`;

--
-- Table structure for table `Companies`
--
CREATE TABLE IF NOT EXISTS `Companies` (
  `CompanyID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `CompanyName` varchar(30) NOT NULL,
  PRIMARY KEY (`CompanyID`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=34 ;

--
-- Table structure for table `LastScan`
--

CREATE TABLE IF NOT EXISTS `LastScan` (
  `ScanID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `LastScan` datetime NOT NULL,
  PRIMARY KEY (`ScanID`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Table structure for table `Notifications`
--

CREATE TABLE IF NOT EXISTS `Notifications` (
  `NotifyID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `NotifyTime` datetime NOT NULL,
  `UserID` varchar(20) NOT NULL,
  `TargetID` int(11) NOT NULL,
  `Message` varchar(100) NOT NULL,
  PRIMARY KEY (`NotifyID`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=55522 ;

--
-- Table structure for table `Pings`
--

CREATE TABLE IF NOT EXISTS `Pings` (
  `PingID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `TargetID` int(11) unsigned NOT NULL,
  `Timestamp` datetime NOT NULL,
  `Status` varchar(255) NOT NULL,
  PRIMARY KEY (`PingID`)

--
-- Table structure for table `PreviousScans`
--

CREATE TABLE IF NOT EXISTS `PreviousScans` (
  `ScanID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `TimeStamp` datetime NOT NULL,
  PRIMARY KEY (`ScanID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `Program`
--

CREATE TABLE IF NOT EXISTS `Program` (
  `ProgramID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ProgramName` varchar(15) NOT NULL,
  `StartDate` date NOT NULL,
  `EndDate` date NOT NULL,
  PRIMARY KEY (`ProgramID`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=13 ;


--
-- Table structure for table `Targets`
--

CREATE TABLE IF NOT EXISTS `Targets` (
  `TargetID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `IPAddress` varchar(15) NOT NULL,
  `CompanyID` int(11) unsigned NOT NULL,
  `Namespace` varchar(30) NOT NULL,
  `SMIVersion` varchar(15) DEFAULT NULL,
  `Product` varchar(30) NOT NULL,
  `Principal` varchar(30) NOT NULL,
  `Credential` varchar(30) NOT NULL,
  `CimomVersion` varchar(30) DEFAULT NULL,
  `InteropNamespace` varchar(30) DEFAULT NULL,
  `Notify` enum('Enabled','Disabled') NOT NULL DEFAULT 'Disabled',
  `NotifyUsers` varchar(12) DEFAULT NULL,
  `ScanEnabled` enum('Enabled','Disabled') NOT NULL DEFAULT 'Enabled',
  `Protocol` varchar(10) NOT NULL DEFAULT 'http',
  `Port` varchar(10) NOT NULL,
  PRIMARY KEY (`TargetID`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=123 ;


--
-- Table structure for table `Users`
--

CREATE TABLE IF NOT EXISTS `Users` (
  `UserID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Firstname` varchar(30) NOT NULL,
  `Lastname` varchar(30) NOT NULL,
  `Email` varchar(50) NOT NULL,
  `CompanyID` int(11) NOT NULL,
  `Active` enum('Active','Inactive') NOT NULL,
  `Notify` enum('Enabled','Disabled') NOT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=81 ;

