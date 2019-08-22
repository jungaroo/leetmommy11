console.log('hi')
$('.search-form').submit(function () {
    $('#loading-gif').show();

    $(".error").remove();
    const checked = [...$('.check-box')].some(box => box.checked);
    if (!checked) {
        $('.search-form').after('<span class="error">Check a cohort box please </span>');
        $('#loading-gif').hide();
        return false;
    }
});


