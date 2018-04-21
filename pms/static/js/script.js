// $(document).ready(function() {
//     $(function() {
//         $('nav a[href^="/' + location.pathname.split("/").slice(-1) + '"]').addClass('active');
//     });
// });

//Highlights the tab of the active page
let activepage = () => {
    let url = location.pathname.split("/").slice(-1);
    let id = `${url}-tab`;
    let active_page = document.getElementById(id);
    let tabs = document.getElementsByClassName('active');
    for(let x=0; x<tabs.length; x++) {
        tabs[x].className -= ' active';
    }
    document.getElementById(id).className += ' active';
};

let toggleQuoteRow = (clicked_id) => {
    let id_num = clicked_id.slice(-1);
    let quote_row_id = `quote-row-${id_num}`;
    let quote_row = document.getElementById(quote_row_id);

    if(quote_row.className == 'hidden') {
        quote_row.className = 'show';
    } else {
        quote_row.className = 'hidden';
    }
};

//Ensures only one status can be chosen at a time
let orderStatusControl = () => {
    try {
        let id_isApproved = document.getElementById('id_isApproved');
        let id_isPending = document.getElementById('id_isPending');
        let id_isDenied = document.getElementById('id_isDenied');

        let updateApproved = () => {
            id_isApproved.checked = true;
            id_isDenied.checked = false;
            id_isPending.checked = false;
        };

        let updatePending = () => {
            id_isApproved.checked = false;
            id_isDenied.checked = false;
            id_isPending.checked = true;
        };

        let updateDenied = () => {
            id_isApproved.checked = false;
            id_isDenied.checked = true;
            id_isPending.checked = false;
        };

        id_isApproved.addEventListener("click", updateApproved);
        id_isPending.addEventListener("click", updatePending);
        id_isDenied.addEventListener("click", updateDenied);
    } catch(TypeError){
        console.log('Not on order page');
    }
};

//Makes sure contract budget is greater than 0.  Front-end form validator
let preventNegativeBudget = () => {
    let prevent = () => {
        if(id_CBudget.value <= 0) {
            id_CBudget.value = 0;
            alert("NOTICE: Budget must be greater than 0.");
        }
    };

    let target = document.getElementById('id_CBudget');
    target.addEventListener("focusout", prevent);
};

let done = false;
let checkComplete = () => {
    let complete = () => {
        done = true;            
    }
    let target = document.getElementById('submit');
    target.addEventListener("click", complete);

};

//Checks to see if quotes are complete
window.onbeforeunload = (done) => {
    if(done) {
        return true;
    }
};

window.onload = callFunctions = () => {
    orderStatusControl();
    preventNegativeBudget();
    checkComplete();
};
