// Menu for Agrotecnico
$(document).ready(
                function() {
                    $(".sublist.hid").hide();
                    //show current category
                    
                    //Show after click
                    $("#category-cont>li>a").click(
                        
                            function () {

                                    $(this).next().show(500);
                            }
                        );
                  $(".sublist").mouseleave(
                        function(){
                        $(this).hide(500);
                            
                        }
                      );
                }
        );
