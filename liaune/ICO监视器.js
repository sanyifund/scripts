var api = 'https://www.tinygrail.com/api/';
function getData(url, callback) {
  if (!url.startsWith('http'))
    url = api + url;
  $.ajax({
    url: url,
    type: 'GET',
    xhrFields: { withCredentials: true },
    success: callback
  });
}
function postData(url, data, callback) {
  var d = JSON.stringify(data);
  if (!url.startsWith('http'))
    url = api + url;
  $.ajax({
    url: url,
    type: 'POST',
    contentType: 'application/json',
    data: d,
    xhrFields: { withCredentials: true },
    success: callback
  });
}
function getICO(id) {
	getData(`chara/initial/users/${id}/1`,function (d, s) {
		var data = d.Value.Items[0];
		var name = data.Name;
		getData(`chara/user/assets/${name}/true`, function (d, s) {
			var data = d.Value;
			for (i = 0; i < data.Initials.length; i++) {
				var CharacterId = data.Initials[i].CharacterId;
				var ico_id = data.Initials[i].Id;
				if(ico_id == id){
					getData(`chara/${CharacterId}`, function (d, s) {
						var Id = d.Value.Id;
						var CharacterId = d.Value.CharacterId;
						var Name = d.Value.Name;
						var Link = 'https://bgm.tv/character/'+ CharacterId;
						var Bonus = d.Value.Bonus;
						var Total = d.Value.Total;
						var Users = d.Value.Users;
						var Begin = d.Value.Begin;
						var End = d.Value.End;
						var SubjectName = d.Value.SubjectName;
						var SubjectLink = 'https://bgm.tv/subjetct'+ d.Value.SubjectId;
						document.write('<tr><td>'+Id +'</td><td><a href="'+Link+'" class="l">'+CharacterId+'</a></td><td>'+Name+'</td><td>'+Bonus+'</td><td>'+Total+'</td><td>'+Users+'</td><td>'+End+'</td></tr>');
					});
				}
			}
		}); 
	}); 
}
function pushup(){
	if(end > start){
		getICO(start);
		start++;
		setTimeout("pushup()",2000);
	}
}
var start=2010;
var end = 2030;
document.write('<table><tbody><tr><th>ICO_Id</th><th>角色Id</th><th>角色名</th><th>新番期数</th><th>筹集金额</th><th>人数</th><th>ICO结束时间</th></tr></tbody><tbody>');
pushup();


















function getUserAssets(callback) {
  getData('chara/user/assets', callback);
}

function getUserInitial(id, callback) {
  getData(`chara/initial/${id}`, function (d, s) {
    callback(d, s);
  });
}

function getInitialUsers(id, page, callback) {
  getData(`chara/initial/users/${id}/${page}`, function (d, s) {
    callback(d, s);
  });
}

function RenderInitialUser(icu) {
  var avatar = normalizeAvatar(icu.Avatar);

  var user = `<div class="user">
              <a target="_blank" href="/user/${icu.Name}"><img src="${avatar}"></a>
              <div class="name">
                <a target="_blank" href="/user/${icu.Name}">${icu.NickName}</a>
                <div class="tag">+${formatNumber(icu.Amount, 0)}</div>
              </div></div>`;

  return user;
}
function normalizeAvatar(avatar) {
  if (!avatar) return '//lain.bgm.tv/pic/user/l/icon.jpg';

  var a = avatar.replace("http://", "//");
  var index = a.indexOf("?");
  if (index >= 0)
    a = a.substr(0, index);

  return a;
}
function loadICOBox(ico) {
  var predicted = caculateICO(ico);
  var end = new Date(ico.End) - (new Date().getTimezoneOffset() + 8 * 60) * 60 * 1000;
  var percent = Math.round(ico.Total / predicted.Next * 100);
  var p = percent > 100 ? 100 : percent;
  percent = formatNumber(percent, 0);
  var predictedBox = '';
  if (predicted.Level > 0)
    predictedBox = `<div class="predicted"><div class="tag lv${predicted.Level}">level ${predicted.Level}</div>预计发行量：约${formatNumber(predicted.Amount, 0)}股 | 发行价：₵${formatNumber(predicted.Price, 2)}</div>`;

  var badge = '';
  if (ico.Type === 1)
    badge = `<span class="badge" title="剩余${ico.Bonus}期额外分红">×${ico.Bonus}</span>`;

  var box = `<div class="title"><div class="text">#${ico.CharacterId} -「${ico.Name}」 ICO进行中${badge}</div><div class="balance"></div></div>
  <div class="desc">
  <div class="bold">已筹集 ₵${formatNumber(ico.Total, 0)} / <span class="sub">下一等级需要₵${formatNumber(predicted.Next, 0)}</span></div>
  <div class="sub">剩余时间：<span id="day"></span><span id="hour"></span><span id="minute"></span><span id="second"></span></div>
  </div>
  ${predictedBox}
  <div class="progress_bar"><div class="progress" style="width:${p}%">${percent}%</div></div>`
  $('#grailBox').append(box);
  countDown(end, function () { loadGrailBox(cid); });

  getInitialUsers(ico.Id, 1, function (d, s) {
    if (d.State === 0) {
      if (d.Value.TotalItems > 0) {
        var desc = `<div class="desc"><div class="bold">参与者 ${d.Value.TotalItems} / <span class="sub">10</span></div></div><div class="users"></div>`;
        $('#grailBox').append(desc);
        for (i = 0; i < d.Value.Items.length; i++) {
          var icu = d.Value.Items[i];
          var user = RenderInitialUser(icu);
          $("#grailBox .users").append(user);
        }
        if (d.Value.TotalPages > 1) {
          var loadMore = `<div class="center_button"><button id="loadMoreButton" class="load_more_button">[加载更多...]</button></div>`
          $("#grailBox .users").after(loadMore);
          $("#loadMoreButton").data('page', 2);
          $("#loadMoreButton").on('click', function () {
            var page = $("#loadMoreButton").data('page');
            getInitialUsers(ico.Id, page, function (d, s) {
              if (d.State === 0) {
                for (i = 0; i < d.Value.Items.length; i++) {
                  var icu = d.Value.Items[i];
                  var user = RenderInitialUser(icu);
                  $("#grailBox .users").append(user);
                }
              }
              $("#loadMoreButton").data('page', page + 1);
              if (d.Value.CurrentPage >= d.Value.TotalPages)
                $(".center_button").hide();
            });
          });
        }
      }
    }

    getUserAssets(function (d, s) {
      if (d.State === 0) {
        var balance = `账户余额：<span>₵${formatNumber(d.Value.Balance, 2)}</span>`;
        $('.title .balance').html(balance);
        getUserInitial(ico.Id, function (d, s) {
          var text = '追加注资请在下方输入金额';
          if (d.State === 0) {
            text = `已注资₵${formatNumber(d.Value.Amount, 2)}，${text}`;
          }
          var trade = `<div class="desc">${text}</div>
        <div class="trade"><input class="money" type="number" min="1000" value="1000"></input><button id="appendICOButton" class="active">确定</button><button id="cancelICOButton">取消</button></div>`;
          $('#grailBox').append(trade);
          $('#appendICOButton').on('click', function () { appendICO(ico.Id) });
          $('#cancelICOButton').on('click', function () { cancelICO(ico.Id) });
        });
      } else {
        addLoginButton($('.title .balance'), function () {
          loadICOBox(ico);
        });
      }
    });
  });
}
function caculateICO(ico) {
  var level = 0;
  var price = 10;
  var amount = 10000;
  var total = 0;
  var next = 100000;

  if (ico.Total < 100000 || ico.Users < 10) {
    return { Level: level, Next: next, Price: 0, Amount: 0 };
  }

  level = Math.floor(Math.sqrt(ico.Total / 100000));
  amount = 10000 + (level - 1) * 7500;
  price = ico.Total / amount;
  next = Math.pow(level + 1, 2) * 100000;

  return { Level: level, Next: next, Price: price, Amount: amount };
}
function formatNumber(number, decimals, dec_point, thousands_sep) {
  number = (number + '').replace(/[^0-9+-Ee.]/g, '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 2 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function (n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.ceil(n * k) / k;
    };

  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  var re = /(-?\d+)(\d{3})/;
  while (re.test(s[0])) {
    s[0] = s[0].replace(re, "$1" + sep + "$2");
  }

  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}
function countDown(end, callback) {
  var now = new Date();
  var times = (end - now) / 1000;
  var timer = setInterval(function () {
    var day = 0;
    var hour = 0;
    var minute = 0;
    var second = 0;
    if (times > 0) {
      day = Math.floor(times / (60 * 60 * 24));
      hour = Math.floor(times / (60 * 60)) - (day * 24);
      minute = Math.floor(times / 60) - (day * 24 * 60) - (hour * 60);
      second = Math.floor(times) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
    }
    // if (day <= 9) day = '0' + day;
    // if (hour <= 9) hour = '0' + hour;
    // if (minute <= 9) minute = '0' + minute;
    // if (second <= 9) second = '0' + second;

    $('span#day').text(day + '天');
    $('span#hour').text(hour + '时');
    $('span#minute').text(minute + '分');
    $('span#second').text(second + '秒');

    now = new Date();
    times = (end - now) / 1000;
  }, 1000)
  if (times <= 0) {
    clearInterval(timer);
    callback();
  }
}