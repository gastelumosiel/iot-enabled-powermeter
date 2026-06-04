def web_page():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerLytix Network Setup</title>

    <style>

    body{
    margin:0;
    padding:0;
    font-family: Arial, Helvetica, sans-serif;
    background:#edf1f0;
    min-height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    }

    /* MAIN CARD */

    form.info{
    width:420px;
    background:white;
    padding:40px;
    border-radius:20px;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    border-top:8px solid #0a9c6b;
    }

    h2{
    margin-top:0;
    margin-bottom:10px;
    color:#0d1635;
    font-size:2rem;
    }

    .subtitle{
    margin-bottom:30px;
    color:#5d6472;
    font-size:1rem;
    }

    label{
    display:block;
    margin-bottom:10px;
    font-weight:bold;
    color:#16213d;
    }

    input[type=text]{
    width:100%;
    padding:16px;
    margin-bottom:24px;
    border:1px solid #cfd5df;
    border-radius:12px;
    box-sizing:border-box;
    font-size:1rem;
    transition:0.2s;
    }

    input[type=text]:focus{
    outline:none;
    border-color:#0a9c6b;
    box-shadow:0 0 0 4px rgba(10,156,107,0.12);
    }

    input.info[type=submit]{
    width:100%;
    background:#0a9c6b;
    color:white;
    padding:16px;
    border:none;
    border-radius:12px;
    cursor:pointer;
    font-size:1.05rem;
    font-weight:bold;
    transition:0.2s;
    }

    input.info[type=submit]:hover{
    background:#08845a;
    }

    /* POPUP */

    .popup-overlay{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,0.4);
    display:none;
    justify-content:center;
    align-items:center;
    }

    .popup{
    width:380px;
    background:white;
    border-radius:20px;
    padding:30px;
    box-shadow:0 10px 30px rgba(0,0,0,0.15);
    animation:fadeIn 0.25s ease;
    }

    .popup h3{
    margin-top:0;
    color:#0d1635;
    font-size:1.5rem;
    }

    .popup p{
    color:#4f5665;
    margin-bottom:12px;
    line-height:1.5;
    }

    .popup-data{
    background:#f4f7f6;
    border-radius:12px;
    padding:15px;
    margin-top:15px;
    margin-bottom:25px;
    }

    .popup-data div{
    margin-bottom:10px;
    word-break:break-word;
    }

    .popup-buttons{
    display:flex;
    gap:12px;
    }

    .popup-buttons button{
    flex:1;
    padding:14px;
    border:none;
    border-radius:12px;
    cursor:pointer;
    font-size:1rem;
    font-weight:bold;
    }

    .edit-btn{
    background:#dde3e8;
    color:#1c2b40;
    }

    .confirm-btn{
    background:#0a9c6b;
    color:white;
    }

    .edit-btn:hover{
    background:#cfd6dd;
    }

    .confirm-btn:hover{
    background:#08845a;
    }

    @keyframes fadeIn{
    from{
        opacity:0;
        transform:translateY(15px);
    }
    to{
        opacity:1;
        transform:translateY(0);
    }
    }

    /* MOBILE */

    @media(max-width:520px){

    form.info{
        width:90%;
        padding:30px;
    }

    .popup{
        width:90%;
    }

    }

    </style>
    </head>

    <body>

    <form class="info" id="wifiForm">

    <h2>Network Setup</h2>

    <div class="subtitle">
        Enter your WiFi credentials to connect your device.
    </div>

    <label for="ssid">SSID / Network Name</label>
    <input type="text" id="ssid" name="ssid">

    <label for="pass">Password</label>
    <input type="text" id="pass" name="pass">

    <input class="info" type="submit" value="Continue">

    </form>

    <!-- CONFIRMATION POPUP -->

    <div class="popup-overlay" id="popupOverlay">

    <div class="popup">

        <h3>Confirm Information</h3>

        <p>
        Please verify that the following network information is correct before continuing.
        </p>

        <div class="popup-data">

        <div>
            <strong>SSID:</strong>
            <span id="confirmSSID"></span>
        </div>

        <div>
            <strong>Password:</strong>
            <span id="confirmPASS"></span>
        </div>

        </div>

        <div class="popup-buttons">

        <button type="button" class="edit-btn" id="editBtn">
            Edit
        </button>

        <button type="button" class="confirm-btn" id="confirmBtn">
            Finalize
        </button>

        </div>

    </div>

    </div>

    <script>

    const form = document.getElementById("wifiForm");
    const popup = document.getElementById("popupOverlay");

    const confirmSSID = document.getElementById("confirmSSID");
    const confirmPASS = document.getElementById("confirmPASS");

    const editBtn = document.getElementById("editBtn");
    const confirmBtn = document.getElementById("confirmBtn");

    /*
    IMPORTANT:
    This preserves the original form structure
    so your Python backend should require
    minimal or no modifications.
    */

    form.addEventListener("submit", function(event){

    event.preventDefault();

    const ssid = document.getElementById("ssid").value;
    const pass = document.getElementById("pass").value;

    confirmSSID.textContent = ssid;
    confirmPASS.textContent = pass;

    popup.style.display = "flex";

    });

    editBtn.addEventListener("click", function(){

    popup.style.display = "none";

    });

    confirmBtn.addEventListener("click", function(){

    popup.style.display = "none";

    /*
        IMPORTANT:
        This submits the ORIGINAL form after confirmation,
        maintaining compatibility with the Python script.
    */

    form.submit();

    });

    </script>

    </body>
    </html>
    """
    return html