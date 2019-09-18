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
function collect(username){
	var url = 'chara/user/assets/'+username+'/true';
	getData(url, function (d, s) {
      var data = d.Value;
	  var my_ico_Initials = {};
	  var my_ico_Characters = {};
      for (i = 0; i < data.Initials.length; i++) {
        var id = data.Initials[i].CharacterId;
        var feed = data.Initials[i].State;
		my_ico_Initials[id] = feed;
      }
      for (i = 0; i < data.Characters.length; i++) {
	    var d = data.Characters[i];
		document.write('<tr><td><a href="https://bgm.tv/character/'+d.Id+'" class="l">'+d.Id+'</a></td><td>'+d.Name+'</td><td>'+d.Rate+'</td><td>'+d.Total+'</td><td>'+username+'</td><td>'+d.State+'</td><tr>');
	  }
	});
}
document.write('<table><tbody><tr><th>ID</th><th>角色</th><th>股息</th><th>总股数</th><th>持有人</th><th>股数</th></tr></tbody><tbody>');
collect('273965');
/*var i = 0;
var users = ['rog_defwang','sakinin','allegray','449550','286852','261227','346114','liaune','496837','weane'];

function checkup(){
	if(i<users.length){
		console.log(users[i]);
		collect(users[i]);
		i++;
		setTimeout("checkup()",3000);
	}
}
document.write('<table><tbody><tr><th>ID</th><th>角色</th><th>股息</th><th>总股数</th><th>持有人</th><th>股数</th></tr></tbody><tbody>');
checkup();*/