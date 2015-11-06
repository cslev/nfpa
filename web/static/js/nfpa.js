
var allcookies = document.cookie.split(";");

   for (var i = 0; i < allcookies.length; i++) {
        var cookie = allcookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
        
    }

function bootstrap_load()
{
	$("[name='my-checkbox']").bootstrapSwitch();
}


function show_help(id)
{
	div_note_mac=document.getElementById(id);
    div_note_mac.style.display='block';
}
  
function hide_help(id)
{
	div_note_mac=document.getElementById(id);
    div_note_mac.style.display='none';
}

function progressBarSim(al) {
    
    var bar = document.getElementById('progressBar');
    var status = document.getElementById('status');
    status.innerHTML = al+"%";
    bar.value = al;
    al++;
    var sim = setTimeout("progressBarSim("+al+")",tl);
    if(al == 100){
      status.innerHTML = "100%";
      bar.value = 100;
      clearTimeout(sim);
      var finalMessage = document.getElementById('finalMessage');
      finalMessage.innerHTML = "Measurement is about to complete";
    }
  }