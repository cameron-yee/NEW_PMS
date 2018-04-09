// $(document).ready(function() {
//     $(function() {
//         $('nav a[href^="/' + location.pathname.split("/").slice(-1) + '"]').addClass('active');
//     });
// });

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