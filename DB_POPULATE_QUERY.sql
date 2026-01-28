-- Use the database
USE CriminalDB;
GO

-- Create the Users table
CREATE TABLE User_Type(
    Type_id INT NOT NULL PRIMARY KEY,
	Type_Name NVARCHAR(50)
);
GO

CREATE TABLE Users(
    user_id NVARCHAR(50) PRIMARY KEY,
    user_password NVARCHAR(50) NOT NULL,
    user_name NVARCHAR(255) NOT NULL,
    user_rank NVARCHAR(50),
    user_department NVARCHAR(50),
    user_type_id INT NOT NULL FOREIGN KEY REFERENCES User_Type(Type_id)
);
GO


CREATE TABLE Login(
    user_id NVARCHAR(50) NOT NULL PRIMARY KEY FOREIGN KEY REFERENCES Users(user_id),
	Type_Name NVARCHAR(50)
);
GO


-- Create the Convicted_Person table
CREATE TABLE Convicted_Person (
    Person_ID INT PRIMARY KEY IDENTITY(1,1),
    CNIC NVARCHAR(15),
    Name NVARCHAR(255) NOT NULL,
    DateOfBirth DATE NOT NULL,
    LastKnownAddress NVARCHAR(255),
    Gender NVARCHAR(10),
    FingerPrintID NVARCHAR(50),
    DNAProfile NVARCHAR(255),
    Charges NVARCHAR(MAX),
    Status NVARCHAR(50),
    Aliases NVARCHAR(255),
    PhysicalDescription NVARCHAR(MAX),
    ArrestHistory NVARCHAR(MAX),
    ConvictionDetails NVARCHAR(MAX),
    IncarcerationDetails NVARCHAR(MAX),
    ParoleDetails NVARCHAR(MAX),
    Remarks NVARCHAR(MAX)
);
GO

-- Create the FIR table
CREATE TABLE FIR (
    FIRno INT PRIMARY KEY IDENTITY(1,1),
    dateofFiling DATE NOT NULL,
    dateofIncident DATE NOT NULL,
    Location NVARCHAR(255) NOT NULL,
    policeStationCode NVARCHAR(100) NOT NULL,
    complainantDetails NVARCHAR(MAX),
    accusedDetails NVARCHAR(MAX),
    witnessDetails NVARCHAR(MAX),
    crimeNature NVARCHAR(100) NOT NULL,
    sectionofLaw NVARCHAR(50) NOT NULL,
    officerDetails NVARCHAR(255) NOT NULL,
    status NVARCHAR(50) NOT NULL
);
GO

CREATE TABLE FIR_Person(
	FIR_No INT NOT NULL FOREIGN KEY REFERENCES FIR(FIRno),
	person_ID INT NOT NULL FOREIGN KEY REFERENCES Convicted_Person(Person_ID),
	PRIMARY KEY (FIR_No,person_ID)
);
GO


-- Create the Person_Request table
CREATE TABLE Person_Request (
    RequestID INT PRIMARY KEY IDENTITY(1,1),
    person_id INT NOT NULL FOREIGN KEY REFERENCES Convicted_Person(Person_ID),
    ApprovalDate DATE,
    approval BIT,
    requestor_user_id NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    approver_user_id NVARCHAR(50) FOREIGN KEY REFERENCES Users(user_id),
    new_CNIC NVARCHAR(15),
    new_name NVARCHAR(255),
    new_dateofbirth DATE,
    new_lastknownaddress NVARCHAR(255),
    new_gender NVARCHAR(10),
    new_fingerprintid NVARCHAR(50),
    new_dnaprofile NVARCHAR(255),
    new_charges NVARCHAR(MAX),
    new_convictiondetails NVARCHAR(MAX),
    new_physicaldescription NVARCHAR(MAX),
    new_arresthistory NVARCHAR(MAX),
    new_incarcerationdetails NVARCHAR(MAX),
    new_paroledetails NVARCHAR(MAX),
    new_status NVARCHAR(50),
    new_remarks NVARCHAR(MAX)
);
GO

-- Create the FIR_Request table
CREATE TABLE FIR_Request (
    RequestID INT PRIMARY KEY IDENTITY(1,1),
    FIRNo INT NOT NULL FOREIGN KEY REFERENCES FIR(FIRNo),
    ApprovalDate DATE,
    approval BIT,
    requestor_user_id NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES Users(user_id),
    approver_user_id NVARCHAR(50) FOREIGN KEY REFERENCES Users(user_id),
    new_date_of_filing DATE,
    new_date_of_incident DATE,
    new_Location NVARCHAR(255),
    new_policeStationCode NVARCHAR(100),
    new_complainantDetails NVARCHAR(MAX),
    new_accusedDetails NVARCHAR(MAX),
    new_witnessDetails NVARCHAR(MAX),
    new_crimeNature NVARCHAR(100),
    new_sectionofLaw NVARCHAR(50),
    new_officerDetails NVARCHAR(255),
    new_status NVARCHAR(50)
);
GO

INSERT INTO User_Type (Type_id, Type_Name) VALUES 
(1, 'Admin'),
(2, 'Operator');
GO

INSERT INTO Users (user_id, user_password, user_name, user_rank, user_department, user_type_id) VALUES 
('admin001', 'pass123', 'John Doe', 'Chief Inspector', 'Crime Investigation', 1),
('op001', 'opPass', 'Jane Smith', 'Sergeant', 'Fraud Division', 2),
('viewer001', 'viewPass', 'Alice Brown', NULL, NULL, 2);
GO

INSERT INTO Login (user_id, Type_Name) VALUES 
('admin001', 'Admin'),
('op001', 'Operator'),
('viewer001', 'Viewer');
GO

INSERT INTO Convicted_Person (
    CNIC, Name, DateOfBirth, LastKnownAddress, Gender, FingerPrintID, DNAProfile, 
    Charges, Status, Aliases, PhysicalDescription, ArrestHistory, ConvictionDetails, 
    IncarcerationDetails, ParoleDetails, Remarks
) VALUES 
('12345-6789012-3', 'Michael Johnson', '1985-06-15', '123 Elm Street', 'Male', 'FP123', 'DNA123',
 'Robbery, Assault', 'Convicted', 'Mike J', '6ft, Scar on left cheek', 'Arrested 3 times', 
 'Sentenced to 10 years', 'Serving in Central Jail', NULL, 'Repeat Offender'),
('98765-4321098-7', 'Emily Davis', '1990-03-22', '456 Maple Avenue', 'Female', 'FP456', 'DNA456',
 'Fraud', 'Released on Bail', 'Emma', '5ft 5in, Blonde Hair', 'Arrested once', 'Pending Trial', 
 NULL, 'Bail Granted', 'Under observation');
GO


INSERT INTO FIR (
    dateofFiling, dateofIncident, Location, policeStationCode, complainantDetails, 
    accusedDetails, witnessDetails, crimeNature, sectionofLaw, officerDetails, status
) VALUES 
('2024-01-15', '2024-01-10', 'Downtown', 'PS001', 'John Doe - 12345-6789012-3', 
 'Michael Johnson - 98765-4321098-7', 'Witness A, Witness B', 'Theft', 'Section 379', 
 'Officer A', 'Open'),
('2024-02-20', '2024-02-18', 'Uptown', 'PS002', 'Jane Doe - 23456-7890123-4', 
 'Emily Davis - 98765-4321098-7', 'Witness C', 'Fraud', 'Section 420', 
 'Officer B', 'Under Investigation');
GO


INSERT INTO FIR_Person (FIR_No, person_ID) VALUES 
(1, 1),  -- FIR No. 1 linked with Person ID 1
(2, 2);  -- FIR No. 2 linked with Person ID 2
GO

SELECT * FROM Users;
SELECT * FROM Convicted_Person;
SELECT * FROM FIR;
SELECT * FROM FIR_Person;





