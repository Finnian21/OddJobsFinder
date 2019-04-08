function myFunction() 
{
    var checkBox = document.getElementById("differentContacts");
    var text = document.getElementById("fields");
    if (checkBox.checked == true)
    {
        text.style.display = "block";
    } 
    else 
    {
        text.style.display = "none";
    }
}
function myFunction2() 
{
    var checkBox = document.getElementById("differentAddress");
    var text = document.getElementById("address");
    if (checkBox.checked == true)
    {
        text.style.display = "block";
    } 
    else 
    {
        text.style.display = "none";
    }
}

function alertRegisteration()
{
    alert("You have registered successfully");
}