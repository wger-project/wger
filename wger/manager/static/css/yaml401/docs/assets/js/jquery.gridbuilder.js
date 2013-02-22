/*
 * jQuery gridBuilder
 * Version 1.2 (26/10/2009)
 *
 * Copyright (c) 2009 Kilian Valkhof (kilianvalkhof.com)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */
"use strict";
(function ($) {
  $.fn.gridBuilder = function (useroptions) {
    return this.each(function () {
      var $this = $(this);

      //init options
      var options = $.extend(
        {id: this.id},
        $.fn.gridBuilder.defaults,
        useroptions
      );

      if ( $.fn.gridBuilder.featureDetection() ) {
		  // build canvas and context
		  var gridCanvas = $.fn.gridBuilder.makeCanvas(options);
		  var gridContext = gridCanvas.getContext("2d");

		  // draw all lines and place them as background
		  $.fn.gridBuilder.drawVertical(gridContext, options);
		  $.fn.gridBuilder.drawHorizontal(gridContext, options);
		  $.fn.gridBuilder.setBackground(this, gridCanvas, options);
	  }
    });
  };

  //Provide defaults
  $.fn.gridBuilder.defaults = {
    color:          '#eee',
    secondaryColor: '#f9f9f9',
    vertical:       18,
    horizontal:     140,
    gutter:         40
  };


  $.fn.gridBuilder.featureDetection = function() {
	  var elem = document.createElement('canvas');
	  return !!(elem.getContext && elem.getContext('2d'));
  };

  // build a canvas the size of the chosen element
  $.fn.gridBuilder.makeCanvas = function (options) {
    var canvas = document.createElement('canvas');
    canvas.id = "gridCanvasFor" + options.id;
    canvas.height = options.vertical;
    canvas.width = options.horizontal + options.gutter;
    return canvas;
  };

  // draw the vertical lines
  $.fn.gridBuilder.drawVertical = function (gridContext, options) {
    if (options.horizontal) {
      gridContext.beginPath();
      for (var x = - (options.gutter/2) - 0.5; x <= options.horizontal + options.gutter; x += options.horizontal) {
        $.fn.gridBuilder.drawSingleLine(gridContext, x, 0, x, options.vertical);
        if (options.gutter > 0) {
          x += options.gutter;
          $.fn.gridBuilder.drawSingleLine(gridContext, x, 0, x, options.vertical);
        }
      }
      $.fn.gridBuilder.draw(gridContext, options.color);

      //draw secondary lines
      if (options.secondaryColor) {
        var xs = (options.gutter/2) + (options.horizontal / 2) - 0.5;
        gridContext.beginPath();
        $.fn.gridBuilder.drawSingleLine(gridContext, xs, 0, xs, options.vertical);
        $.fn.gridBuilder.draw(gridContext, options.secondaryColor);
      }
    }
  };

  // draw the horizontal lines
  $.fn.gridBuilder.drawHorizontal = function (gridContext, options) {
    if (options.vertical) {
      var y = options.vertical - 0.5;
      gridContext.beginPath();
      $.fn.gridBuilder.drawSingleLine(gridContext, 0, y, options.horizontal + options.gutter, y);
      $.fn.gridBuilder.draw(gridContext, options.color);

      //draw secondary lines
      if (options.secondaryColor) {
        var ys = (options.vertical / 2) - 0.5;
        gridContext.beginPath();
        $.fn.gridBuilder.drawSingleLine(gridContext, 0, ys, options.horizontal + options.gutter, ys);
        $.fn.gridBuilder.draw(gridContext, options.secondaryColor);
      }
    }
  };

  // draw single line
  $.fn.gridBuilder.drawSingleLine = function (gridContext, x, y,newx,newy) {
    gridContext.moveTo(x, y);
    gridContext.lineTo(newx, newy);
  };
  // draw elements on the canvas
  $.fn.gridBuilder.draw = function (gridContext, color) {
    gridContext.strokeStyle = color;
    gridContext.stroke();
  };

  // set as background
  $.fn.gridBuilder.setBackground = function (element, gridCanvas, options) {
    var canvasData = gridCanvas.toDataURL();
    $(element).css({
      "background-image": "url(" + canvasData + ")",
      "background-repeat":"repeat"
    });
  };

  // remove canvas element, get rid of background image
  $.fn.destroyGrid = function (useroptions) {
    return this.each(function () {
      var $this = $(this);
      $this.css({"background-image": "none"});
      $("gridCanvasFor" + $this.id).remove();
    });
  };
}(jQuery));

