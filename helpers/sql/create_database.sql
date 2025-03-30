CREATE TABLE zuschauerumfrage_2025_shakespeare_in_hollywood (
    Bilddatei NVARCHAR(50) UNIQUE,
    Datum DATETIME,
    Altersgruppe NVARCHAR(15),
    Postleitzahl NVARCHAR(5),
    Wiederholungskunde NVARCHAR(5),
    Verwandter NVARCHAR(5),
    Werbung_Zeitung NVARCHAR(5),
    Werbung_Flyer NVARCHAR(5),
    Werbung_Facebook NVARCHAR(5),
    Werbung_Freunde NVARCHAR(5),
    Werbung_Plakate NVARCHAR(5),
    Werbung_Instagram NVARCHAR(5),
    Werbung_Radio NVARCHAR(5),
    Werbung_Sonstiges NVARCHAR(100)
);