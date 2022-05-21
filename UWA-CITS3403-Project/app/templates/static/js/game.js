let index = 1, number = 0, list = [], id;

function signup(e) {
    e.preventDefault();
    let username = $('#signup_username').val();
    let password = $('#signup_password').val();
    $.ajax({
        url: '/sign_up',
        type: 'POST',
        data: {'username': username, 'password': password},
        dataType: 'json',
        success: function (data) {
            id = data.id;
            if (data.result) {
                $('#signin_signup').click().hide();
                $('#username_text').text(username);
            }
        },
    });
}

function signin(e) {
    e.preventDefault();
    let username = $('#signin_username').val();
    let password = $('#signin_password').val();
    $.ajax({
        url: '/sign_in',
        type: 'POST',
        data: {'username': username, 'password': password},
        dataType: 'json',
        success: function (data) {
            id = data.id;
            if (data.result) {
                $('#signin_signup').click().hide();
                $('#username_text').text(username);
            }
        },
    });
}

function save() {
    $.ajax({
        url: '/save',
        type: 'POST',
        data: {'id': id, 'words': list.toString(), 'number': number},
        dataType: 'json',
        success: function (data) {
        },
        complete: function () {
            statistics();
        },
    });
}

function statistics() {
    $.ajax({
        url: '/statistics',
        type: 'POST',
        data: {'id': id},
        dataType: 'json',
        success: function (data) {
            $('#s_1').text(data.total_played);
            $('#s_2').text(data.max_number);
            $('#s_3').text(data.max_number_time);
            $('#s_4').text(data.average_number);
            $('#s_5').text(data.world_rank);
            $('#s_6').text(data.no1_username);
            $('#s_7').text(data.no1_max_number);
            $('#s_8').text(number);
            for (let i = 0; i < number; i++) {
                $('#s_9').append('<span>' + list[i] + '</span>');
            }
        },
        complete: function () {
            $('#statistics').modal('show');
        },
    });
}

function init() {
    $('#l1').text('F');
    $('#l2').text('O');
    $('#l3').text('U');
    $('#l4').text('R');
    $('#c1').text('F');
    $('#c2').text('O');
    $('#c3').text('U');
    $('#c4').text('R');
    $('.char').css('border-style', 'solid');
    $('#start').text('GO').on('click', start);
}

function next() {
    $.ajax({
        url: '/next_word',
        type: 'POST',
        dataType: 'json',
        success: function (data) {
            let word = data.word;
            for (let i = 1; i < 5; i++) {
                $('#l' + i).text(word.charAt(i - 1));
            }
            $('.char').text('').css('border-style', 'dashed');
            index = 1;
        },
    });
}

function check() {
    let word = '';
    for (let i = 1; i < 5; i++) {
        word += $('#c' + i).text();
    }
    $.ajax({
        url: '/check',
        type: 'POST',
        data: {'word': word},
        dataType: 'json',
        success: function (data) {
            let result = data.result;
            if (result) {
                next();
                $('#mark').css({opacity: 0.0, visibility: "visible"})
                    .animate({opacity: 1.0})
                    .css({opacity: 1.0, visibility: "hidde"})
                    .animate({opacity: 0.0}, {
                        duration: 300,
                        complete: function () {
                            number++;
                            $('#start').text(number);
                            list.push(word);
                            $('#list').append('<span>' + word + '</span>');
                        }
                    });
            } else {
                next();
            }
        }
    });
}

function play() {
    $('#c' + index).text($(this).text()).css('border-style', 'solid');
    if (index === 4) {
        check();
    } else {
        index++;
    }
}

function startTimer(counter) {
    var interval = setInterval(function () {
        counter--;
        if (counter <= 0) {
            clearInterval(interval);
            $('.box').off('click', play);
            $('#timer').slideUp();
            $('#list').slideDown();
            init();
            if (id) {
                save();
            } else {
                $('#login_user').hide();
                $('#s_8').text(number);
                for (let i = 0; i < list.length; i++) {
                    $('#s_9').append('<span>' + list[i] + '</span>');
                }
                $('#statistics').modal('show');
            }
        } else {
            $('#timer').text(counter);
        }
    }, 1000);
}

function start() {
    number = 0;
    list = [];
    $('#s_9').empty();
    next();
    $('#start').text(number).off('click');
    $('#list').slideUp().empty();
    $('#timer').text('60').slideDown();
    $('.box').on('click', play);
    $('.char').css('border-style', 'dashed');
    startTimer(60);
}

$(function () {
    $('#signup').on('click', signup);
    $('#signin').on('click', signin);
    $('.box').off('click', play);
    $('#start').on('click', start);

    $('.dropdown-menu').on('click', function (event) {
        var events = $._data(document, 'events') || {};
        events = events.click || [];
        for (var i = 0; i < events.length; i++) {
            if (events[i].selector) {
                if ($(event.target).is(events[i].selector)) {
                    events[i].handler.call(event.target, event);
                }
                $(event.target).parents(events[i].selector).each(function () {
                    events[i].handler.call(this, event);
                });
            }
        }
        event.stopPropagation();
    });
});

function shareWords(words) {
    navigator.share({
            title: 'My lucky words today:',
            text: words,
            url: 'https://teaching.csse.uwa.edu.au/units/CITS3403/#project',
            hashtags: ['Four Leaf Clover Puzzle Game', 'Lucky Words']
        },
        {
            copy: true,
            email: true,
            print: true,
            sms: true,
            messenger: true,
            facebook: true,
            whatsapp: true,
            twitter: true,
            linkedin: true,
            telegram: true,
            skype: true,
            language: 'en'
        })
        .then(_ => console.log('shared.'))
        .catch(error => console.log('error:', error));
}
