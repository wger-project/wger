/*
 * This file is part of wger Workout Manager.
 *
 * wger Workout Manager is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * wger Workout Manager is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 */

/*
 * wger Nutriton functions
 */

function update_ingredient_value(url)
{
    form_data = $('#nutritional-values-form').serializeArray();
    $.post(url, form_data, function(data) {

        console.log(data);
        // Show any validation errors
        $('#calculator-errors').html('');
        if (data['errors'])
        {
            $.each(data['errors'], function(index, value) {
                $('#calculator-errors').append('<p class="ym-message">'+value+'</p>');
            });
        }

        // Replace the nutritional values
        $('#value-energy').html(parseFloat(data['energy']).toFixed(2));
        $('#value-protein').html(parseFloat(data['protein']).toFixed(2));
        $('#value-carbohydrates').html(parseFloat(data['carbohydrates']).toFixed(2));
        $('#value-carbohydrates-sugar').html(parseFloat(data['carbohydrates_sugar']).toFixed(2));
        $('#value-fat').html(parseFloat(data['fat']).toFixed(2));
        $('#value-fat-saturated').html(parseFloat(data['fat_saturated']).toFixed(2));
        $('#value-fibres').html(parseFloat(data['fibres']).toFixed(2));
        $('#value-sodium').html(parseFloat(data['sodium']).toFixed(2));
        });
}

function init_ingredient_detail(url)
{
    // Prevent the form from being sent
    $('#nutritional-values-form').submit(function(e) {
        e.preventDefault();
    });

    $('#id_amount').keyup(function(){
        update_ingredient_value(url);
    });

    $('#id_unit').change(function(){
        update_ingredient_value(url);
    });
}



/*
 * Update the user's preferences
 */
function init_english_ingredients()
{
    $("#ajax-english-ingredients").click(function(e) {
        e.preventDefault();

        // Update the status icon and the data attribute
        switch_to = $('#english-ingredients-status').data('showIngredients') == 'true' ? 0 : 1;
        if ( switch_to == 1 )
        {
            $('#english-ingredients-status').attr("src", "/static/images/icons/status-on.svg");
            $('#english-ingredients-status').data('showIngredients', 'true');
        }
        else if ( switch_to == 0 )
        {
            $('#english-ingredients-status').attr("src", "/static/images/icons/status-off.svg");
            $('#english-ingredients-status').data('showIngredients', 'false');
        }

        // Update the settings
        $("#ajax-info").load('/' + get_current_language() + "/workout/api/user-preferences?do=set_english-ingredients&show=" + switch_to);
    });
}
