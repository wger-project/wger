$(document).ready(function() {

	var domscripts = {

		init: function init () {

			var self = this;

			self.installStickyMenu();
			self.installTabs();
			self.installSyntaxHighlighting();
			self.installGrid();
			self.installFormSwitcher();
		},

		installStickyMenu: function installStickyMenu () {

			var header      = $('body > header'),
				headings    = $('#main h2'),
				nav         = $('nav#level2'),
				stickyClass = 'fix';

			if (nav.find('.ym-hlist').length > 0 ) {

				// install smallscreen menu
				var menu =	'<li><label for="ym-smnav" style="padding: 0 0.5em; color: rgba(255,255,255,.8)">Navigation:</label> '+
							'<select id="ym-smnav" style="font-size: 16px;"><option value="0" selected="selected" disabled="disabled">Go to ...</option>';
				var items = nav.find('a');
				$.each(items, function(key){
					menu += '<option data-target="'+$(this).attr('href')+'">'+$(this).text()+'</option>';
				});
				menu += '</select></li>';

				var smnav = $(menu).appendTo(nav.find('ul')).hide();

				$(window).bind('resize',function(){
					var width = $(window).width();
					
					if (width > 740) {
						smnav.siblings().show();
						smnav.hide();
					} else {
						smnav.siblings().hide();
						smnav.show();
					}
				});
				
				$(smnav).bind('change', function(){
					var target = $(this).find('option:selected').data('target');
					nav.find('a[href='+target+']').trigger('click');
				});

				$(document).bind('scroll',function(){
					var hOffset = header.offset().top+header.height(),
						top     = $(document).scrollTop(),
						trigger = false;

					// make it sticky ...
					if (hOffset < top) {
						if (nav.data(stickyClass) !== true) {
							nav.addClass(stickyClass).data(stickyClass,true);
						}
					} else {
						if (nav.data(stickyClass) !== false) {
							nav.removeClass(stickyClass).data(stickyClass,false);
						}
					}

					var nOffset = nav.height();

					// adjust active menu-item from scroll-value
					$.each(headings, function(key){
						var id        = '#'+$(this).attr('id'),
							offset    = $(this).offset().top,
							pos       = offset - top,
							targetPos = 0;

						if (nav.hasClass(stickyClass) === true) {
							targetPos = 2*nav.height();
						}

						if (pos > targetPos) {
							nav.find('a[href="'+id+'"]').parent().prev().addClass('active').siblings().removeClass('active');
							return false;
						} else if (pos < targetPos && pos > targetPos - nOffset) {
							nav.find('a[href="'+id+'"]').parent().addClass('active').siblings().removeClass('active');
							return false;
						}
					});
				});

				// initial check for scroll-status ...
				$(document).trigger('scroll');
				$(window).trigger('resize');

				if ($('body').hasClass('doc') === true) {

					var stateObj = { page: "index" };

					// jump to a named anchor ...
					$('#level2 a').bind('click', function(event){
						event.preventDefault();

						var id      = $(this).attr('href'),
							pos     = $(id).offset().top,
							nHeight = nav.height() + 6; // 6px whitespace

						// set active menu-item ...
						$(this).parent()
							.addClass('active')
							.siblings()
							.removeClass('active');

						$(id).focus();

						// adjust scroll-value
						if (nav.hasClass(stickyClass) === true) {
							$(document).scrollTop(pos-nHeight);
						} else {
							$(document).scrollTop(pos-2*nHeight);
						}
						// update URL id fragment
						history.pushState(stateObj, "docs", "index.html"+id);
					});
				}
			}
		},

		installTabs: function installTabs () {

			// standard behavoir in YAML docs
			$('.jquery_tabs:not([data-sync])').accessibleTabs({
				fx:"show",
				fxspeed: '',
				syncheights: false,
				tabhead: 'h5',
				tabbody:'.tab-content'
			});

			// "accessible tabs" sync example
			$('.jquery_tabs[data-sync="true"]').accessibleTabs({
				fx:"show",
				fxspeed: '',
				syncheights: true,
				tabhead: 'h5',
				tabbody:'.tab-content'
			});
		},

		installSyntaxHighlighting: function installSyntaxHighlighting () {
			var highlightStyle = "peachpuff";

			if (jQuery.fn.snippet) {
				$("pre.htmlCode").snippet("html", {style: highlightStyle});
				$("pre.cssCode").snippet("css", {style: highlightStyle});
				$("pre.jsCode").snippet("javascript", {style: highlightStyle});
			}
		},

		installGrid: function installGrid () {

			// vertical rhythm lines for typography section ...
			if (jQuery.fn.gridBuilder) {
				$(".v-grid").gridBuilder({
					color: '#eee', // color of the primary gridlines
					secondaryColor: '#f9f9f9', // color of the secondary gridlines
					vertical: 21, // height of the vertical rhythm
					horizontal: 2000, // width of horizontal strokes
					gutter: 0 // width of the gutter between strokes
				});
			}
		},

		installFormSwitcher: function installFormSwitcher () {
			$('#formswitch [type="checkbox"]').prop('checked', true);
			$('#formswitch [type="radio"]:first').prop('checked', true);
			
			$('#formswitch').change(function(event){
				var target = event.target,
					type   = $(target).data('type');
				
				if ($(target).attr('type') == 'radio') {
					$('#demo-form1, #demo-form2').removeClass('ym-columnar');
					$('#demo-form1, #demo-form2').removeClass('ym-full');
					$('#demo-form1, #demo-form2').addClass(type);
				}
				if ($(target).attr('type') == 'checkbox') {
					if ($(target).prop('checked') === true) {
						$('#demo-form1, #demo-form2').addClass('linearize-form');
					} else {
						$('#demo-form1, #demo-form2').removeClass('linearize-form');
					}
				}
			});
		}
	};

	domscripts.init();
});

//check for deep links
$(window).load(function() {
	var fragment = location.href.split('#'),
		nav      = $('nav#level2');
			
	if (fragment.length > 0) {
		$(nav.find('a[href="#'+fragment[1]+'"]')).trigger('click');
	}
});
