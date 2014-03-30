/*
Copyright (C) 2011 by Kevin Nam Truong, Daniel Steinberg, Debasish Das, Juan Pineda, Melissa Miranda, and Victoria Pan 

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

`THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Authors:
  Juan Pineda, GitHub: NilNullZip, juan@logician.com
*/

function on_submit(username) {
    $('#loading').show();

    $('#topic').empty();
    
    var url = "/cgi-bin/StalkerBotCGI.py";

    logging = false;

    if (logging) console.log(username);

    var status = 0;

    var ajaxArgs = {
        url: url,
        dataType: 'json',
        data:{ userid:username},
        success:function(data) {
            if (logging) console.log(data);
            var blockCount = 0;

            if (data == null) {
                status = 0;
                }
            else if (data.length == 0) {
                status = 1;
                }
            else

            // Once around for each article/comment

            $.each(data, function(index, element) {
                status = 2;

                // element has format ['tag', ['sentiment1'(,'sentiment2',...)]]

                tag = element[0][0];
                sentimentList = element[1];
                commentText = htmlEncode(element[2]);
                commentLink = element[3];
                articleLink = element[4];
                articleTitle = htmlEncode(element[5]);
                commentId = element[6];
                if (logging) console.log(element, tag, sentimentList);

                var tags = "";
                $.each(element[0], function(index, tag) {
                    if (index != 0) tags = tags + ", ";
                    tags = tags + tag;
                });

                // Append article title

                $('#topic').append(''
                        + '<a href="' + articleLink + '" style="text-decoration:none" class="article_link" title="' + tags + '">'
                        + articleTitle
                        + '</a>' );

                // Once around for each sentiment

                $.each(sentimentList, function(index, sentiment) {
                    sentimentAdj = {"Confidence" : "confident",
                            "Anxiety"    : "anxious",
                            "Compassion" : "compassionate",
                            "Hostility"  : "hostile",
                            "Depression" : "depressed",
                            "Happiness"  : "happy"};

                    if (blockCount >= 5) {
                        $('#topic').append('<br/><br/>');
                        blockCount = 0;
                    }

                    // Append sentiment icon

                    var li = $('<li class="object ' + commentId + '">'
                            + '<img src="img/' + sentimentAdj[sentiment] + '.png" alt="sentiment"/>'
                            + '<div class="sentiment">' + sentimentAdj[sentiment] + '</div>'
                            + '</li>');

                    if (logging) console.log(li.user());
                    $('#topic').append(li);
                    blockCount++;
                });

                $('.' + commentId).wrapAll('<a href="' + commentLink + '" class="hn_link" title="' + commentText + '"/>');

                $('#topic').append('<br/><br/><br/>');
                blockCount = 0;
            });
            $('.hn_link').bt({
                padding: 20,
                width: 500,
                spikeLength: 15,
                spikeGirth: 40,
                cornerRadius: 20,
                fill: 'rgba(0, 0, 0, .8)',
                strokeWidth: 3,
                strokeStyle: '#ef4136',
                cssStyles: {color: '#FFF'},
                positions: ['top', 'bottom'],
                activeClass: 'hn_link_active',
                centerPointX: .60,
                overlap: -10,
            });
            $('.article_link').bt({
                padding: 15,
                width: 325,
                spikeLength: 0,
                spikeGirth: 0,
                cornerRadius: 20,
                fill: 'rgba(0, 0, 0, .8)',
                strokeWidth: 3,
                strokeStyle: '#ef4136',
                cssStyles: {color: '#FFF', fontWeight: 'bold'},
                positions: ['top', 'bottom'],
                overlap: -7,
            });
        },
        complete: function() {
            $('#loading').hide();
            if (status == 0) {
                $('#topic').append('<br/>User not found. If you believe this incorrect, please let us know.<br/>');
                }
            else if (status == 1) {
                $('#topic').append('<br/>That one had nothing to say. Try another.<br/>');
                }
        }
    };

    // the following no longer works as of March 15, 2014
    //$.ajax(ajaxArgs);
    
}

$('#st_form').submit(function(e) {
    e.preventDefault();
    var username = $("#st_input", this).val();
    $.address.value(username);
});

$.address.init(function() {
    // Initializes the plugin
    $('a.home_link').address();
}).change(function(event) {
    $('#topic').empty();
    $('#topic').append('<br/><div style="text-align: left; margin: 0 auto; width: 600px">Stalkerbot no longer works. As of March 15, 2014, HNSearch was shut down. There are no current plans to transition Stalkerbot to use the new HN API powered by Algolia.</div><img src="img/depressedTransparent.png" style="width: 200px"><br/>');
    return;

    var username = event.value.substr(1);
    if (username == '') {
        $('#topic').empty();
        $("#st_input").val('');
    } else {
        $("#st_input").val(username);
        on_submit(username);
    }
});

$('a.home_link').click(function(){
    $('#topic').empty();
    $("#st_input").val('');
});

function htmlEncode(str)
{
    str = str.replace(/&/g, "&amp;");
    str = str.replace(/>/g, "&gt;");
    str = str.replace(/</g, "&lt;");
    str = str.replace(/"/g, "&quot;");
    str = str.replace(/'/g, "&#039;");
    return str;
}
