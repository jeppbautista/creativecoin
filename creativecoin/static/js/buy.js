$('input[type=radio]').on('change', function () {
    if (this.value == 'gcash') {
        $('#coinsph').hide();
        $('#gcash').show();
    }
    else if (this.value == 'coinsph') {
        $('#gcash').hide();
        $('#coinsph').show();
    }
});

$('input#quantity').on('change', function(){
    let quantity = this.value;
    let amount_php = 0;
    let amount_usd = 0;

    if (quantity == ''){
        $('input#quantity').val(1);
        quantity = 1;
    }

    quantity = parseFloat(quantity);
    amount_php = parseFloat($('#amount-php').data()['amount']);
    amount_usd = parseFloat($('#amount-usd').data()['amount']);

    amount_php = (quantity * amount_php).toFixed(2);
    amount_usd = (quantity * amount_usd).toFixed(2)

    $('#amount-php').html(amount_php);
    $('#amount-usd').html(amount_usd);
    $('input[name = "amount_php"]').val(amount_php);
    $('input[name = "amount_usd"]').val(amount_usd);
});