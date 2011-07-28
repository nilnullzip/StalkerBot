$('#st_form').submit(function(e) {
    e.preventDefault();
    $('#loading').show();
    
    $('#topic').empty();
    var val = $("#st_input", this).val();
    var url = "/cgi-bin/StalkerBotCGI.py";

    console.log(val);
                
    function htmlEncode(str)
    {
        str = str.replace(/&/g, "&amp;");
        str = str.replace(/>/g, "&gt;");
        str = str.replace(/</g, "&lt;");
        str = str.replace(/"/g, "&quot;");
        str = str.replace(/'/g, "&#039;");
        return str;
    }

    $.ajax({
        url: url,
        dataType: 'json',
        data:{ userid:val},
        success:function(data) {
            console.log(data);
            var blockCount = 0;

            $.each(data, function(index, element) {
                // element has format ['tag', ['sentiment1'(,'sentiment2',...)]]
                var tags = "";
		$.each(element[0], function(index, tag) {
                     if (index != 0) tags = tags + ", ";
                     tags = tags + tag;
                });
                    tag = element[0][0]
                    // tag = element[0];
                    sentimentList = element[1];
                    commentText = htmlEncode(element[2]);
                    commentLink = element[3];
                    articleLink = element[4];
                    articleTitle = htmlEncode(element[5]);
                    console.log(element, tag, sentimentList);

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

			var li = $('<li class="object"><a href="' + articleLink + '" style="text-decoration:none" class="article_link" title="' + tags + '"><div class="title">'
//			var li = $('<li class="object"><a href="' + articleLink + '" style="text-decoration:none"><div class="tag">'
                            + articleTitle + '</div></a>'
			    + '<a href="' + commentLink + '" class="hn_link" title="' + commentText + '"><img src="img/'
			    + sentimentAdj[sentiment] + '.png" alt="sentiment"/></a><div class="sentiment">'
			    + sentimentAdj[sentiment] + '</div></li>');
			console.log(li.val());
			$('#topic').append(li);
			blockCount++;
                    });
                $('#topic').append('<br/><br/>');
                $('#topic').append('<br/><br/>');
                blockCount = 0;
            });
            $(document).ready(function(){
            $(".tag").ellipsis();
            });
            $('.hn_link').bt({
                padding: 20,
                width: 275,
                spikeLength: 20,
                spikeGirth: 20,
                cornerRadius: 20,
                fill: 'rgba(0, 0, 0, .8)',
                strokeWidth: 3,
                strokeStyle: '#ef4136',
                cssStyles: {color: '#FFF'},
                positions: ['right', 'left']
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
                positions: ['top']
            });
        },
        complete: function() {
            $('#loading').hide();
        }
    });
});

