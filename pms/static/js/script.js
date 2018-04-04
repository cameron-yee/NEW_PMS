$(document).ready(function() {
    $(function() {
        $('nav a[href^="/' + location.pathname.split("/").slice(-1) + '"]').addClass('active');
    });
});