
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
	var div_note_mac=document.getElementById(id);
    div_note_mac.style.display='block';
}
  
function hide_help(id)
{
	var div_note_mac=document.getElementById(id);
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

function email_service_changed(tagname)
{
    var email_service = document.getElementById(tagname);
    var status = email_service.options[email_service.selectedIndex].value;
    var ids = ["email_from", "email_to", "email_server", "email_port",
               "email_username", "email_password", "email_timeout"];
    var ids_len=ids.length;

    if (status == "false")
    {
        for (var i = 0; i < ids_len; i++)
        {
            var element = document.getElementById(ids[i]);
            element.disabled = true;

        }
    }
    else
    {
     for (var i = 0; i < ids_len; i++)
        {
            var element = document.getElementById(ids[i]);
            element.disabled = false;

        }
    }
}

function disable_elements(tagname)
{
    var ids;
    var main_indicator = document.getElementById(tagname);
    var status = main_indicator.options[main_indicator.selectedIndex].value;
//    alert(tagname);
    if (tagname == "control_nfpa")
    {
        ids = ["control_path", "control_args",
               "control_vnf_inport", "control_vnf_outport", "control_mgmt"];
    }
    else if (tagname == "email_service")
    {
        ids = ["email_from", "email_to", "email_server", "email_port",
                   "email_username", "email_password", "email_timeout"];

    }
    else
    {
        alert("Unable to disable further corresponding elements...sorry");
        return
    }
//    console.log(ids.toString());
    var ids_len=ids.length;

    if (status == "false")
    {
        for (var i = 0; i < ids_len; i++)
        {
            var element = document.getElementById(ids[i]);
            element.disabled = true;

        }
    }
    else
    {
     for (var i = 0; i < ids_len; i++)
        {
            var element = document.getElementById(ids[i]);
            element.disabled = false;

        }
    }
}