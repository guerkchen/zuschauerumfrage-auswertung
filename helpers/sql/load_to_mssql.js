const sql = require('mssql');
const fs = require('fs');
const csv = require('csv-parser');
const moment = require('moment');
require('dotenv').config();

// Azure SQL-Datenbankverbindungsdetails
const config = {
    user: process.env.user,
    password: process.env.password,
    server: process.env.server,
    database: process.env.database,
    options: {
        encrypt: true,
        trustServerCertificate: true,
        enableArithAbort: true,
        connectionTimeout: 30000
    },

    debug: true,
};

async function loadCSVToSQL(pool, filePath, tableName) {
    return new Promise((resolve, reject) => {
        let rows = [];

        fs.createReadStream(filePath)
            .pipe(csv({ separator: ';' }))
            .on('data', (row) => {
                if (row.Datum) {
                    row.Datum = moment(row.Datum, 'DD.MM.YYYY').format('YYYY-MM-DD');
                }
                rows.push(row);
            })
            .on('end', async () => {
                if (rows.length === 0) {
                    console.log(`❌ Keine Daten in ${filePath}`);
                    resolve();
                    return;
                }

                let columns = Object.keys(rows[0]);
                let placeholders = columns.map((col, i) => `@param${i}`).join(', ');
                let query = `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES (${placeholders})`;

                for (let row of rows) {
                    let request = pool.request();
                    columns.forEach((col, i) => request.input(`param${i}`, row[col]));
                    try {
                        await request.query(query);
                    } catch (err) {
                        if (err.code === 'EREQUEST' && err.number === 2627) { // Unique constraint violation
                            console.log(`⚠️  Duplikat gefunden: ${row.Bilddatei}`);
                        } else {
                            console.error(`❌ Fehler beim Einfügen von ${row.Bilddatei}:`, err);
                            reject(err);
                        }
                    }
                }

                console.log(`✅ Erfolgreich importiert: ${filePath}`);
                resolve();
            }).on('error', (err) => {
                console.error(`❌ Fehler beim Lesen der Datei ${filePath}:`, err);
                reject(err);
            });
    });
}

// Liste der CSV-Dateien
const csvFiles = ["../../output/auswertung_2025-03-23_11-24-40.csv",
    "../../output/auswertung_2025-03-23_11-29-20.csv"];
const tableName = 'zuschauerumfrage_2025_shakespeare_in_hollywood';

(async () => {
    let pool;
    try {
        pool = await sql.connect(config);
        for (let file of csvFiles) {
            await loadCSVToSQL(pool, file, tableName);
        }
    } catch (err) {
        console.error(`❌ Fehler beim Verarbeiten der Dateien:`, err);
    } finally {
        if (pool) {
            await pool.close();
            console.log('✅ Verbindung geschlossen');
        }
    }
})();
