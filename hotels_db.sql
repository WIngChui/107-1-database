
CREATE TABLE `Contact` (
  `email` VARCHAR(255)  PRIMARY KEY
);

CREATE TABLE `Phone` (
  `email` VARCHAR(255) NOT NULL,
  `phoneNo` VARCHAR(255) NOT NULL,
  PRIMARY KEY (email, phoneNo),
  FOREIGN KEY (`email`) REFERENCES `Contact` (`email`) ON UPDATE CASCADE
);

CREATE TABLE `Reservation` (
  `reservationNo` INTEGER(8) ZEROFILL PRIMARY KEY AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `checkinDate` DATE NOT NULL,
  `checkoutDate` DATE NOT NULL,
  `totalPrice` INTEGER NOT NULL,
  `guestNum` INTEGER NOT NULL,
  `guestFirstName` VARCHAR(255) NOT NULL,
  `guestLastName` VARCHAR(255) NOT NULL,
  `dateCreated` DATE NOT NULL,
  `cardID` VARCHAR(20) NOT NULL,
  `cardOwner` VARCHAR(255) NOT NULL,
  `dueDate` VARCHAR(5) NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  FOREIGN KEY (`email`) REFERENCES `Contact` (`email`) ON UPDATE CASCADE
);

CREATE TABLE `CancellationRequest` (
  `reservationNo` INTEGER(8) ZEROFILL NOT NULL,
  `dateCreated` DATE NOT NULL,
  `reason` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  PRIMARY KEY(reservationNo, dateCreated),
  FOREIGN KEY (`email`) REFERENCES `Contact` (`email`) ON UPDATE CASCADE,
  FOREIGN KEY (`reservationNo`) REFERENCES `Reservation` (`reservationNo`) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE `Room` (
  `roomNo` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `type` VARCHAR(255) NOT NULL,
  `unitFee` INTEGER NOT NULL,
  `limit` INTEGER NOT NULL
);

CREATE TABLE `Record` (
  `reservationNo` INTEGER(8) ZEROFILL NOT NULL,
  `roomNo` INTEGER NOT NULL,
  PRIMARY KEY(reservationNo, roomNo),
  FOREIGN KEY (`reservationNo`) REFERENCES `Reservation` (`reservationNo`) ON UPDATE CASCADE ON DELETE SET CASCADE,
  FOREIGN KEY (`roomNo`) REFERENCES `Room` (`roomNo`)
);

