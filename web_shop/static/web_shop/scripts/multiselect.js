 //Select multiple
$(document).ready(
function()  {
//Multiselect for attributevalues of productvariant
$('.multiselect_attrs').multiselect(
                {
                numberDisplayed: 10,
                nonSelectedText: "---",
                label: function(element) {
                            var tmp = $(element).html();
                            return tmp.substring(tmp.indexOf('-') +1, tmp.length-1);
                          },
                 onChange: function(element, checked) {
                             var parent = $(element).parent();
                             var mselect = parent.parent(); //Multiselect object
                             //manually select
                             if (checked) {
                                 $(element).attr('selected', 'selected'); //select manually
                                 // If there's a an option already selected from this optiongroup
                                 // don't allow this option to be selected
                                 if (parent.children("option[selected='selected']").length > 1) {
                                    alert("Error: Solo puede seleccionar un valor para cada atributo");
                                    mselect.multiselect('deselect', $(element).prop('value'));
                                    $(element).removeAttr('selected'); //deselect manually
                                 }
                             }
                             else {
                                    $(element).removeAttr('selected'); //deselect manually
                             }

                            }

                }
                );

});
