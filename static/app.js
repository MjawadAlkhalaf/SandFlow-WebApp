const uploadButton = document.getElementById("uploadButton");

const folderButton = document.getElementById("choosePadFolder")

const clearButton = document.getElementById("clearTable")


// ------------------------------------
// TABULATOR TABLE
// ------------------------------------

const table = new Tabulator("#resultsTable", {

    layout: "fitColumns",

    height: "600px",

    movableColumns: false,

    selectableRange: 1,

    selectableRangeClearCells: true,

    clipboard: true,

    clipboardCopyStyled: false,

    clipboardCopyRowRange: "range",

    clipboardPasteParser: "range",

    clipboardPasteAction: "range",

    clipboardCopyConfig: {
        rowHeaders: false,
        columnHeaders: false
    },

    editTriggerEvent: "dblclick",

    columns: [

        {
            title: "Silo",
            field: "silo",
            editor: "input"
        },

        {
            title: "Sand Type",
            field: "sandType",
            editor: "input"
        },

        {
            title: "Carrier",
            field: "carrier",
            editor: "input"
        },

        {
            title: "Weight",
            field: "weight",
            editor: "input"
        },

        {
            title: "BOL",
            field: "bol",
            editor: "input"
        },

        {
            title: "Truck",
            field: "truck",
            editor: "input"
        },

        {
            title: "PO",
            field: "po",
            editor: "input"
        },

        {
            title: "Date",
            field: "date",
            editor: "input"
        },

        {
            title: "Time",
            field: "time",
            editor: "input"
        },

        {
            title: "Facility",
            field: "facility",
            editor: "input"
        },

        {
            title: "Source",
            field: "source",

            formatter: function(cell) {

                const rowData = cell.getRow().getData();

                return `
                    <a href="#"
                       onclick="window.open(
                           '${rowData.source}',
                           'ticketWindow',
                           'width=900,height=1000'
                       ); return false;">
                        ${rowData.filename}
                    </a>
                `;
            },

            headerSort: false
        }
    ]
});

document.addEventListener("keydown", function(event) {

    if (
        event.target.tagName === "INPUT" ||
        event.target.tagName === "TEXTAREA"
    ) {
        return;
    }

    const selectedCells = table.getRanges();

    if (selectedCells.length === 0) {
        return;
    }

    if (
        event.key.length === 1 &&
        !event.ctrlKey &&
        !event.altKey &&
        !event.metaKey
    ) {
        const cells = selectedCells[0].getCells();

        if (cells.length === 0) {
            return;
        }

        const cell = cells[0][0];

        if (cell) {
            cell.edit();

            setTimeout(() => {
                const input = cell.getElement().querySelector("input");

                if (input) {
                    input.value = event.key;

                    input.setSelectionRange(
                        input.value.length,
                        input.value.length
                    );
                }
            }, 0);

            //event.preventDefault();
        }
    }
});

document.addEventListener("keydown", function(event) {

    const ranges = table.getRanges();

    if (ranges.length === 0) {
        return;
    }

    const cells = ranges[0].getCells();

    if (cells.length === 0 || cells[0].length === 0) {
        return;
    }

    const selected = cells[0][0];

    if (
        event.target.tagName === "INPUT" ||
        event.target.tagName === "TEXTAREA"
    ) {

        let nextCell = null;

        if (event.key === "ArrowRight") {
            const rowCells = selected.getRow().getCells();
            const currentIndex = rowCells.indexOf(selected);

            if (currentIndex < rowCells.length - 1) {
                nextCell = rowCells[currentIndex + 1];
            }
        }

        else if (event.key === "ArrowLeft") {
            const rowCells = selected.getRow().getCells();
            const currentIndex = rowCells.indexOf(selected);

            if (currentIndex > 0) {
                nextCell = rowCells[currentIndex - 1];
            }
        }

        else if (event.key === "ArrowUp") {
            const previousRow = selected.getRow().getPrevRow();

            if (previousRow) {
                nextCell = previousRow.getCell(selected.getColumn().getField());
            }
        }

        else if (event.key === "ArrowDown") {
            const nextRow = selected.getRow().getNextRow();

            if (nextRow) {
                nextCell = nextRow.getCell(selected.getColumn().getField());
            }
        }

        if (nextCell) {

            event.preventDefault();

            selected.cancelEdit();

            setTimeout(() => {

                table.deselectRange();

                table.addRange(
                    nextCell.getElement()
                );

            }, 0);
        }
    }
});

// ------------------------------------
// UPLOAD BUTTON
// ------------------------------------

uploadButton.addEventListener("click", uploadTicket);


// ------------------------------------
// UPLOAD TICKETS
// ------------------------------------

// drag and dop ticket upload
const ticketDropZone = document.getElementById("ticketDropZone");
const ticketFile = document.getElementById("ticketFile");

let files = [];

// changing file name when pressing button instead of drag and drop
ticketFile.addEventListener("change", function() {
    files = ticketFile.files;
    showSelectedFiles();
});

// drag function
ticketDropZone.addEventListener("dragover", function(event) {
    event.preventDefault();
    ticketDropZone.classList.add("drag-over");
});

// drop functions
ticketDropZone.addEventListener("dragleave", function() {
    ticketDropZone.classList.remove("drag-over");
});

ticketDropZone.addEventListener("drop", function(event) {
    event.preventDefault();

    ticketDropZone.classList.remove("drag-over");

    const droppedFiles = event.dataTransfer.files;


    //asigning dropped files to main variable
    files = droppedFiles;
    showSelectedFiles();
});

//show file name in drag and drop window
function showSelectedFiles() {

    if (files.length === 1) {
        document.getElementById("ticketFileName").textContent =
            files[0].name;
    }

    else if (files.length > 1) {
        document.getElementById("ticketFileName").textContent =
            `${files[0].name} + ${files.length - 1} more`;
    }
}


// boolean to indicate if upload ticket is clicked
let running = false;

async function uploadTicket() {

    //Prevent double clicking
    if(running === true) {
        alert("Patience!!!")

        return;
    }

    //retreiving silo number
    const silo = document.getElementById("silo").value;

    //retreiving sand type from dropdown list
    const sandType = document.getElementById("sandType").value;

    // Joining Silo with the number input
    const siloTableInput = `Silo ${silo}`;

    //retreiving file object
    const fileInput = document.getElementById("ticketFile");

    //retreiving the files uploaded
    if (files.length === 0){
        files = fileInput.files;
        
    }


    //fallback in case no file was chosen
    if (files.length === 0) {

        alert("Please select at least one ticket.");

        return;
    }

    running = true;

    //Current time (time of upload)
    const currTime = new Date().toLocaleTimeString("en-US",{hour12: false,hour: "2-digit", minute: "2-digit"});

    //current Date
    const currDate = new Date().toLocaleDateString();

    //looping through files uploaded
    for (const file of files) {

        //initial formData
        const formData = new FormData();

        //appending uploading file
        formData.append("file",file);

        //sending file to backend process ticket and retreiving response
        const response = await fetch( "/process-ticket", { method: "POST", body: formData });

        //fall back in case there was an issue processing
        if (!response.ok) {

            alert(
                `Failed to process ${file.name}`
            );

            continue;
        }


        //process file results
        const result = await response.json();

        //logging to console
        console.log(result);


        // ------------------------------------
        // File type check
        // If response contains the variable tickets (pdf)

        if (result.tickets) {
            
            //looping through pdf ticket results and adding to table
            for (const pdfTicket of result.tickets) {

                addTicketRow(
                    siloTableInput,
                    sandType,
                    pdfTicket.ticket,
                    result.filename,
                    pdfTicket.source_url,
                    currDate,
                    currTime,
                    pdfTicket.invalid
                );
            }
            running = false;
        }


        // Jpeg
        // No Tickets variable found in response so add Jpeg

        else {

            addTicketRow(
                siloTableInput,
                sandType,
                result.ticket,
                result.filename,
                result.source_url,
                currDate,
                currTime,
                result.invalid
            );
            running = false;
        }
    }
}


// Add tickets per row
function addTicketRow(
    silo,
    sandType,
    ticket,
    filename,
    sourceUrl,
    date,
    time,
    invalid
) {

    table.addRow({

        silo: silo,

        sandType: sandType,

        carrier: ticket.carrier,

        weight: ticket.weight,

        bol: ticket.bol,

        truck: ticket.truck,

        po: ticket.po,

        date: date,

        time: time,

        facility: ticket.facility,

        source: sourceUrl,

        filename: filename,

        invalid: invalid
    });
}

//assigning pad folder button
folderButton.addEventListener("click", assignPad)

let padFolder = null;

//choosing pad folder to generate CSV
async function assignPad() {

    //prompt user to choose pad folder
    padFolder = await window.showDirectoryPicker();

    //retreiving pad name from folder path
    document.getElementById("padFolderName").textContent = padFolder.name;

    console.log(padFolder.name);
}

//clear Table
clearButton.addEventListener("click", clearTable)

async function clearTable() {

    table.clearData();
}

//generate CSV button
const csvButton = document.getElementById("generateCSV");
csvButton.addEventListener("click", generateCSV);

async function generateCSV() {

    //fallback if no path folder is chosen
    if (!padFolder) {
        alert("Please choose a pad folder first.");
        return;
    }

    //populate padname
    const padName = padFolder.name;

    //intial tickets stored json file
    let existingTickets = [];

    const jsonFileName = `${padName}_SandTicket.json`;


    try {
            //retrieving file handle   
            const jsonHandle = await padFolder.getFileHandle(jsonFileName);

            //retreiving file
            const jsonFile = await jsonHandle.getFile();

            //reading json content
            const jsonText = await jsonFile.text();

            //converting JSON text into a JavaScript value/object
            existingTickets = JSON.parse(jsonText);

        }
        catch (error) {
            
            //If no Json file assume a new pad
            existingTickets = [];

        }


        const qcTickets =
            table.getData();


        const saveData = {
            pad_name: padName,
            tickets: qcTickets, //table tickets
            existing_tickets: existingTickets //json tickets
        };

        
        const response = await fetch("/generate-csv",
        {
            method: "POST",
            headers: { "Content-Type": "application/json"},
            body: JSON.stringify(saveData)
        });


        if (!response.ok) {
            alert("Failed to process ticket data");
            return;
        }
        
        results = await response.json();
        
        if (!results.success) {

            const messages = results.duplicates.map(duplicate => {

                return `BOL ${duplicate.bol} - ${duplicate.type} - Rows ${duplicate.rows.join(", ")}`;

            });

            //clear old row highlights
            table.getRows().forEach(row => {

                row.getElement()
                .style.backgroundColor = "";

            });


            //highlight duplicate rows
            for (const duplicate of results.duplicates) {

                for (const rowNumber of duplicate.rows) {

                    const row =
                        table.getRows()[rowNumber - 1];

                    if (row) {

                        row.getElement()
                        .style.backgroundColor = "red";

                    }
                }
            }
            alert(
                "Duplicate tickets found:\n\n" +
                messages.join("\n")
            );

            return;
        }
        //success path: remove any old red rows
        table.getRows().forEach(row => {

            row.getElement()
            .style.backgroundColor = "";

        });

        //retreive json file and create one if none exist
        const jsonHandle = await padFolder.getFileHandle( jsonFileName, {create: true});
        
        //open file to write
        const writable = await jsonHandle.createWritable();
        
        //get output from python results
        const jsonOutput = JSON.stringify(results.tickets, null, 4);
        
        //write results to json
        await writable.write(jsonOutput);
        
        await writable.close();

        //csv generating
        const csvFileName = `${padName}_SandTicket.csv`;
        
        //retrieve csv and create one if none exist
        const csvHandle = await padFolder.getFileHandle( csvFileName,{ create: true });

        //open file to write
        const csvWritable = await csvHandle.createWritable();

        //write csv from python results
        await csvWritable.write(results.csv);

        await csvWritable.close();

        console.log(results);

        alert(results.message);

}

//field validation
const validateBttn = document.getElementById("Validate Tickets");
validateBttn.addEventListener("click", validateTickets)

const validationModal = document.getElementById("validationModal");

let currTickets = [];
let index = 0;

function validateTickets() {
    
    currTickets = table.getRows();

    if (currTickets.length === 0){
        alert("No Tickets to validate")
        return;

    }
    

    validationModal.style.display = "flex";

    loadValidationRow(index);


}


// Load a ticket into the popup
function loadValidationRow(index) {

    // Get current  row
    const currentRow = currTickets[index];

    // Get that row's data
    const rowData = currentRow.getData();

    // retreiving row information in validation pop-up
    //setting null values to empty cells for easier editing
    document.getElementById("validateSandType").value = rowData.sandType;

    document.getElementById("validateCarrier").value = rowData.carrier === "null" ? "" : rowData.carrier;

    document.getElementById("validateWeight").value = rowData.weight === 0 ? "" : rowData.weight;

    document.getElementById("validateBol").value = rowData.bol === "null" ? "" : rowData.bol;

    document.getElementById("validateTruck").value = rowData.truck === "null" ? "" : rowData.truck;

    document.getElementById("validatePo").value = rowData.po === "null" ? "" : rowData.po;

    document.getElementById("validateFacility").value = rowData.facility === "null" ? "" : rowData.facility;

    

    // Ticket source
    type = rowData.source.split('.').pop().toLowerCase();
    
  
    document.getElementById("validationSource").src = rowData.source + "#zoom=60";;
    
}

//loading next ticket
const nextValidationButton = document.getElementById("nextValidation");
nextValidationButton.addEventListener("click", nextTicket);

function nextTicket(){
    
    
    if (index < currTickets.length - 1) {

        saveTicket();

        index = index + 1;
        loadValidationRow(index);
        
    }
}


//loading previous ticket
const previousValidationButton = document.getElementById("previousValidation");
previousValidationButton.addEventListener("click", previousTicket);

function previousTicket(){
    
    if (index > 0) {

        saveTicket();

        index = index - 1;
        loadValidationRow(index);
   
    }
}

//saving and populating rows
function saveTicket() {

    const currentRow = currTickets[index];

    currentRow.update({
        sandType: document.getElementById("validateSandType").value,
        carrier: document.getElementById("validateCarrier").value,
        weight: document.getElementById("validateWeight").value,
        bol: document.getElementById("validateBol").value,
        truck: document.getElementById("validateTruck").value,
        po: document.getElementById("validatePo").value,
        facility: document.getElementById("validateFacility").value
    
    });

}

// closing validation popup and resetting index
const closeValidationButton = document.getElementById("closeValidation");

closeValidationButton.addEventListener("click", closeValidation);

function closeValidation() {

    saveTicket();
    index = 0;
    validationModal.style.display = "none";
    // optional: clear the preview
    document.getElementById("validationSource").src = "";
}

//////////// CSV Ticket matching

const csvDropZone = document.getElementById("csvDropZone");
const csvInput = document.getElementById("csvFile");

let csv = null;


// File selected using Browse CSV
csvInput.addEventListener("change", function() {

    csv = csvInput.files[0];

    showCSVFile();
});


// Drag over
csvDropZone.addEventListener("dragover", function(event) {

    event.preventDefault();

    csvDropZone.classList.add("drag-over");
});


// Drag leave
csvDropZone.addEventListener("dragleave", function() {

    csvDropZone.classList.remove("drag-over");
});


// Drop CSV
csvDropZone.addEventListener("drop", function(event) {

    event.preventDefault();

    csvDropZone.classList.remove("drag-over");

    const droppedCSV = event.dataTransfer.files[0];

    csv = droppedCSV;

    showCSVFile();
});


// Show file name
function showCSVFile() {

    document.getElementById("csvFileName").textContent = csv.name;
}


let matchedRecordsTable = null;
let unmatchedRecordsTable = null;
let candidateTable = null;
let row_index = null;
let result = null;


document.getElementById("xiq-import").addEventListener("click", match_xiq)

async function match_xiq() {
    
    // Make sure CSV is selected
    if (csv === null) {
        alert("Please upload XIQ CSV");
        return;
    }
    


    // Send CSV and current Tabulator data to fastapi
    const formData = new FormData();

    // appending uploaded csv
    formData.append("xiq_export", csv);

    const tableData = table.getData();

    // reformatting headers to match backend headers
    const formattedTable = tableData.map(row => ({
        "Silo": row.silo,
        "Sand Type": row.sandType,
        "Carrier": row.carrier,
        "Weight": row.weight,
        "BOL": row.bol,
        "Truck": row.truck,
        "PO": row.po,
        "Date": row.date,
        "Time": row.time,
        "Facility": row.facility,
        "Source": row.source
    }));

    // reformatting current table to json format
    const table_json = JSON.stringify(formattedTable);

    // sending current table to fastapi
    formData.append("currentTable", table_json);

    // sending info to match-xiq-csv function in app.py
    const response = await fetch("/match-xiq-csv", {method: "POST", body: formData});

    //collecting response
    result = await response.json();

    console.log(result);

    //  Open Match Review 
    document.getElementById("matchReviewModal").classList.add("open");

    // creating matched record table in the pop-up
    matchedRecordsTable = new Tabulator("#matchedRecordsTable", {

        data: result.matched_with_order,

        layout: "fitColumns",
        height: "250px",
        
        selectableRange: true,
    

        clipboard: true,
        clipboardCopyRowRange: "range",

        clipboardCopyConfig: {
            rowHeaders: false,
            columnHeaders: false,
            columnGroups: false
        },

        columns: [
            { title: "Silo", field: "Silo" },
            { title: "Sand Type", field: "Sand Type" },
            { title: "Carrier", field: "Carrier" },
            { title: "Weight", field: "Weight" },
            { title: "BOL", field: "BOL" },
            { title: "Truck", field: "Truck" },
            { title: "PO", field: "PO" },
            { title: "Date", field: "Date" },
            { title: "Time", field: "Time" },
            { title: "Facility", field: "Facility" },
            { title: "Order ID", field: "order_id" },
            { title: "Stage", field: "stage" }
        ]
    });

    // creating unmatched table records in pop up
    unmatchedRecordsTable = new Tabulator("#unmatchedSandflowTable", {

        data: result.unmatched_table_tickets,

        layout: "fitColumns",
        height: "250px",
        
        selectableRange: true,
    

        clipboard: true,
        clipboardCopyRowRange: "range",

        clipboardCopyConfig: {
            rowHeaders: false,
            columnHeaders: false,
            columnGroups: false
        },

        columns: [
            { title: "Sand Type", field: "Sand Type" },
            { title: "Carrier", field: "Carrier" },
            { title: "Weight", field: "Weight" },
            { title: "BOL", field: "BOL" },
            { title: "Truck", field: "Truck" },
            { title: "PO", field: "PO" },
            
        ]
    });

    // unmatched count
    document.getElementById("unmatchedCount").textContent = result.unmatched_table_tickets.length;


    // creating initial candidate tabulator table for likely candidates
    candidateTable = new Tabulator("#candidateTable", {
    layout: "fitColumns",
    height: "220px",

    selectableRange: true,
        

    clipboard: true,
    clipboardCopyRowRange: "range",

    clipboardCopyConfig: {
        rowHeaders: false,
        columnHeaders: false,
        columnGroups: false
    },

    columns: [
        { title: "BOL", field: "BOL" },
        { title: "Weight", field: "Weight" },
        { title: "Truck", field: "Truck" },
        { title: "PO", field: "PO" },
        { title: "Carrier", field: "Carrier" },
        { title: "Order ID", field: "order_id" },
        { title: "Stage", field: "stage" },
        { title: "Score", field: "score" }
    ]
    });

    
    // connecting row click to unmatched table and displaying candidate table
    unmatchedRecordsTable.on("rowClick", function (e,row) {

        
        document.getElementById("selectedOrderId").textContent = "-";

        document.getElementById("selectedStage").textContent = "-";

        const fields = ["BOL","Weight","Truck","PO","Carrier","Sand Type"];

        // resetting xiq fields to null when switching to unmatched table
        for (const field of fields) {

            const comparisonRow = document.querySelector(`.comparison-row[data-field="${field}"]`);
            
            comparisonRow.querySelector(".xiq-value").textContent = "-";

            comparisonRow.querySelector(".comparison-status").textContent = "-";
            
        }

        // Save previously selected row
        if (row_index !== null) {
            updateTableXIQ(row_index);
        }

        // resetting row
        row_index = row;

        // Now switch selection to unmatched row
        selectedRow = row_index.getData();
        
        // populating table label
        document.getElementById("candidateSourceBol").textContent = selectedRow.BOL;

        // displaying ticket picture for the row clicked
        document.getElementById("matchTicketPreview").src = selectedRow.Source;

        // setting the fields to ticket info

        document.getElementById("editSandflowBol").value = selectedRow.BOL;
        
        document.getElementById("editSandflowWeight").value = selectedRow.Weight;
        document.getElementById("editSandflowTruck").value = selectedRow.Truck;
        document.getElementById("editSandflowPo").value = selectedRow.PO;
        document.getElementById("editSandflowCarrier").value = selectedRow.Carrier;
        document.getElementById("sandflowSandTypeDisplay").textContent = selectedRow["Sand Type"] ;

        
        

        // populating ticket label
        document.getElementById("selectedSourceBol").textContent = selectedRow.BOL;
        

        //filtering candidate table by bol value clicked and sorting by score
        const selectedCandidates = result.candidates.filter(candidate => candidate.source_bol === selectedRow.BOL).sort((a, b) => b.score - a.score);

        
        // populating table
        candidateTable.setData(selectedCandidates);

        
    });

    // populating matched and duplicate count
    document.getElementById("matchedCount").textContent = result.matched_with_order.length;
    document.getElementById("duplicateCount").textContent = result.duplicates.length;

    matchedRecordsTable.on("rowClick", function (e,row) {
        
        if (row_index !== null) {
            updateTableXIQ(row_index);
        }

        row_index = row;

        candidateTable.clearData();

        selectedRow = row_index.getData();

        // displaying ticket picture for the row clicked
        document.getElementById("matchTicketPreview").src = selectedRow.Source;

        // setting the fields to ticket info
        document.getElementById("editSandflowBol").value = selectedRow.BOL;
        
        document.getElementById("editSandflowWeight").value = selectedRow.Weight;
        document.getElementById("editSandflowTruck").value = selectedRow.Truck;
        document.getElementById("editSandflowPo").value = selectedRow.PO;
        document.getElementById("editSandflowCarrier").value = selectedRow.Carrier;
        document.getElementById("sandflowSandTypeDisplay").textContent = selectedRow["Sand Type"] ;
        
         
        // populating ticket label
        document.getElementById("selectedSourceBol").textContent = selectedRow.BOL;

        const fields = ["BOL","Weight","Truck","PO","Carrier","Sand Type"];

        const matchedXiqRow = result.matched_csv.find(xiqRow => xiqRow.BOL === selectedRow.BOL);

        if (matchedXiqRow) {

            for (const field of fields) {

                const comparisonRow = document.querySelector(`.comparison-row[data-field="${field}"]`);
                
                comparisonRow.querySelector(".xiq-value").textContent = matchedXiqRow[field];

                const status = comparisonRow.querySelector(".comparison-status");

                if (field === "Sand Type") {
                    status.textContent = "-";
                }
                else if (field === "Weight") {

                    status.textContent = selectedRow.weight_bool ? "Match" : "Mismatch";

                    // removing existing style
                    status.classList.remove("match", "mismatch","neutral");

                    // adding styling to match and mismatch
                    status.classList.add(selectedRow.weight_bool ? "match" : "mismatch");

                }
                else if (field === "Truck") {

                    status.textContent = selectedRow.truck_bool ? "Match" : "Mismatch";

                    // removing existing style
                    status.classList.remove("match", "mismatch","neutral");

                    // adding styling to match and mismatch
                    status.classList.add(selectedRow.truck_bool ? "match" : "mismatch");
                }
                else if (field === "PO") {
                    status.textContent = selectedRow.po_bool ? "Match" : "Mismatch"

                     // removing existing style
                    status.classList.remove("match", "mismatch","neutral");

                    // adding styling to match and mismatch
                    status.classList.add(selectedRow.po_bool ? "match" : "mismatch");
                }
                else if (field === "BOL") {

                    // handling duplicates
                    if (result.duplicates.some(duplicate => duplicate.BOL === selectedRow.BOL)) {

                        status.textContent = "Duplicate";

                        // removing existing style
                        status.classList.remove("match", "mismatch","neutral");

                        // adding styling to match and mismatch
                        status.classList.add("mismatch");

                        const dupes = [];

                        //finding duplicate bols order ids
                        for (const duplicate of result.duplicates) {

                            if (duplicate.BOL === selectedRow.BOL) {

                                dupes.push(duplicate.order_id);

                            }
                        }

                        alert("Bol: " + selectedRow.BOL + " Found in Orders:\n" + dupes.join("\n"));
                    }
                    else {
                        status.textContent = "Match";

                        // removing existing style
                        status.classList.remove("match", "mismatch","neutral");

                        // adding styling to match and mismatch
                        status.classList.add("match");
                    }
                }
                else {
                    status.textContent = "Match";

                     // removing existing style
                    status.classList.remove("match", "mismatch","neutral");

                    // adding styling to match and mismatch
                    status.classList.add("match");
                }

            }
            // Populate Order ID and Stage 
            document.getElementById("selectedOrderId").textContent = matchedXiqRow.order_id;

            document.getElementById("selectedStage").textContent = matchedXiqRow.stage;


        
        }

        // update main table
        updateMainTable(matchedRecordsTable.getData());
        updateMainTable(unmatchedRecordsTable.getData());
        


    })

};

// updating xiqtable as they are edited
function updateTableXIQ(row_index){

    row_index.update({
        Carrier: document.getElementById("editSandflowCarrier").value,
        Weight: document.getElementById("editSandflowWeight").value,
        BOL: document.getElementById("editSandflowBol").value,
        Truck: document.getElementById("editSandflowTruck").value,
        PO: document.getElementById("editSandflowPo").value
    });


}

// updating main table after editing on xiq pop-up
function updateMainTable(reviewRows) {

    // existing rows in main window
    const mainRows = table.getRows();

    for (const reviewRow of reviewRows) {

        // finding the bol to edit on the main
        const mainRow = mainRows.find(row => row.getData().source === reviewRow.Source);

        
        if (mainRow) {
            mainRow.update({
                sandType: reviewRow["Sand Type"],
                carrier: reviewRow.Carrier,
                weight: reviewRow.Weight,
                bol: reviewRow.BOL,
                truck: reviewRow.Truck,
                po: reviewRow.PO
            });
        }
    }
}

// refresh button
const refreshButton = document.getElementById("refreshMatch");

refreshButton.addEventListener("click", refresh);

async function refresh() {

    // save the last ticket being edited
    if (row_index !== null) {
        updateTableXIQ(row_index);
    }

    // update main table
    updateMainTable(matchedRecordsTable.getData());
    updateMainTable(unmatchedRecordsTable.getData());

    row_index = null;

    // call match xiq again
    await match_xiq();
}

// close xiq window pop up
const closeButtonTop = document.getElementById("closeMatchReview");
closeButtonTop.addEventListener("click", closeXIQ);

const closeButtonBottom = document.getElementById("closeMatchReviewBottom")
closeButtonBottom.addEventListener("click", closeXIQ)

function closeXIQ () {

    matchReviewModal.classList.remove("open");
    document.getElementById("matchTicketPreview").src = "";
    
}

// option button to populate sandflow fields with xiq values (mass execute fields)
const useXIQButton = document.getElementById("use-xiq");
useXIQButton.addEventListener("click", populateWithXIQ);


function populateWithXIQ() {

    // fall back if no row is selected
    if (row_index === null) {

        return;
    }

    // get current data for row select
    const rowData = row_index.getData();

    // finding the ticket info in the matched csv
    const xiqRow = result.matched_csv.find(row => row.BOL === rowData.BOL);

    console.log("FOUND XIQ ROW:", xiqRow);

    if (!xiqRow) {
        return;
    }

    // assigning xiq values to sandflow fields
    document.getElementById("editSandflowCarrier").value = xiqRow.Carrier;
    document.getElementById("editSandflowWeight").value = xiqRow.Weight;
    document.getElementById("editSandflowBol").value = xiqRow.BOL;
    document.getElementById("editSandflowTruck").value = xiqRow.Truck;
    document.getElementById("editSandflowPo").value = xiqRow.PO;
}


