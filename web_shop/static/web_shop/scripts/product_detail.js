$(document).ready(
        function() {
            /*Quantity input controls*/
            $('.qty_ctrl').click(
                function () {
                    var val = parseInt($('#id_quantity').attr('value'));
                    var add = parseInt($(this).attr('data-q'));
                    $('#id_quantity').attr('value', Math.max(1, val + add));
                }
                
                );
            /*Img thumbnail*/
            $('.product-gallery-item').click(
                    function(){
                        $('#product-carousel').carousel($(this).index());
                    }
                );

            /*Submit Form via Ajax*/
            $('#cartadd_btn').click(
                function() {
                    $('this').addClass('disabled');

                    $('#product_frm .alert').removeClass('alert-success alert-danger');
                    $('#product_frm .alert').addClass('hidden');
                    $.ajax(
                        {
                         type: "POST",
                         url: document.URL,
                         data: $("#product_frm").serialize(),
                         success: function(data)
                         {
                            $('this').removeClass('disabled');
                            $('#product_frm .alert').removeClass('hidden');
                            if (data == 'SUCCESS') {
                                $('#product_frm .alert').html(message['add_success']);
                                $('#product_frm .alert').addClass('alert-success').fadeIn(300);
                                //Show cart
                                $('#viewcart_modal .modal-body iframe').attr('src', '/shop/cart?popup=1&t='+new Date().getTime());
                                $('#viewcart_modal').modal();   
                            }
                            else {
                                $('#product_frm .alert').html(message['add_error']);
                                $('#product_frm .alert').addClass('alert-danger').hide().fadeIn(300);
                            }
                         }
                        }
                        );
                    return false;
                });

        }
    );


