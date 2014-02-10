module.exports = function(grunt) {

	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),

		// remove all files from yaml folder
		clean: ['yaml'],

		// compile YAML build
		compass: {
			build: {
				options: {
					sassDir        : 'sass/static-build',
					cssDir         : 'yaml',
					importPath     : 'sass',
					imagesDir      : 'yaml',
					outputStyle    : 'expanded',
					noLineComments : true
				}
			},
			docs: {
				options: {
					sassDir        : 'sass/docs',
					cssDir         : 'docs',
					importPath     : 'sass',
					imagesDir      : 'yaml',
					outputStyle    : 'expanded',
					noLineComments : true
				}
			},
			css: {
				options: {
					sassDir        : 'sass/css',
					cssDir         : 'css',
					importPath     : 'sass',
					imagesDir      : 'yaml',
					outputStyle    : 'expanded',
					noLineComments : true
				}
			}
		},

		jshint: {
			options: {
				curly: true,
				eqeqeq: true,
				immed: true,
				latedef: true,
				newcap: true,
				noarg: true,
				sub: true,
				undef: true,
				unused: true,
				boss: true,
				eqnull: true,
				browser: true,
				globals: {
					jQuery: true
				}
			},
			gruntfile: {
				src: 'Gruntfile.js',
				options: {
					globals: {
						module: true
					}
				}
			},
			yaml: [
				'yaml/core/**/*.js'
			],
			addons: [
				'yaml/add-ons/**/*.js'
			]
		},

		'string-replace': {
			stripCharset: {
				files: {
					'./': ['yaml/**/*.css','docs/assets/**/*.css']
				},
				options: {
					replacements: [{
						pattern     : /@charset "utf-8";\cM\cJ/ig,
						replacement : ''
					},
					{
						pattern     : /@charset "utf-8";\cJ/ig,
						replacement : ''
					}]
				}
			},
			setNamespace: {
				files: {
					'./': 'yaml/**/*.css'
				},
				options: {
					replacements: [{
						pattern     : /\.ym-/ig,
						replacement : '.<%= pkg.yamlPrefix %>'
					}]
				}
			},
			setVersion: {
				files: {
					'./': ['yaml/**/*.css','docs/assets/**/*.css']
				},
				options: {
					replacements: [{
						pattern     : /### version ###/ig,
						replacement : '<%= pkg.version %>'
					}]
				}
			},
			// needed for misconfigured Windows systems that don't force UTF8 output correctly ...
			winUTF8fix: {
				files: {
					'./': ['yaml/**/*.css','docs/assets/**/*.css']
				},
				options: {
					replacements: [{
						pattern     : /├ñ/ig,
						replacement : 'ä'
					},
					{
						pattern     : /├ä/ig,
						replacement : 'Ä'
					},
					{
						pattern     : /├Â/ig,
						replacement : 'ö'
					},
					{
						pattern     : /├û/ig,
						replacement : 'Ö'
					},
					{
						pattern     : /├╝/ig,
						replacement : 'ü'
					},
					{
						pattern     : /├£/ig,
						replacement : 'Ü'
					},
					{
						pattern     : /├ƒ/ig,
						replacement : 'ß'
					}]
				}
			}
		},

		cssmin: {
			compress: {
				options: {
					banner: '/*! <%= pkg.name %> v<%= pkg.version %> (<%= grunt.template.today("yyyy-mm-dd") %>) */\n'
				},
				files: [{
					expand : true,           // Enable dynamic expansion.
					cwd    : 'yaml/',        // Src matches are relative to this path.
					src    : ['core/*.css','add-ons/rtl-support/core/*.css'],   // Actual pattern(s) to match.
					dest   : 'yaml/',        // Destination path prefix.
					ext    : '.min.css'      // Dest filepaths will have this extension.
				}]
			}
		},

		copy: {
			main: {
				files: [
					{expand: true, cwd: 'sass/yaml-sass/', src: ['**/*.js'], dest: 'yaml/'}, // makes all src relative to cwd
					{expand: true, cwd: 'sass/yaml-sass/', src: ['**/*.png', '**/*.gif', '**/*.jpg'], dest: 'yaml/'} // makes all src relative to cwd
				]
			}
		},

		watch: {
			files: 'sass/**/*.scss',
			tasks: 'compass'
		}

	});

	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-compass');
	grunt.loadNpmTasks('grunt-string-replace');
	grunt.loadNpmTasks('grunt-contrib-cssmin');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.loadNpmTasks('grunt-contrib-copy');

	// Default Task: Compile defined subfolders in sass/ ('static-build' excluded)
	grunt.registerTask('default', ['clean', 'copy', 'compass:css', 'compass:docs']);

	// Build YAML
	grunt.registerTask('build',  ['clean', 'copy', 'compass', 'string-replace', 'cssmin','jshint']);
	// Build YAML and don't remove @charset rules
	grunt.registerTask('build-utf8',  ['clean', 'copy', 'compass', 'string-replace:setNamespace', 'string-replace:setVersion', 'string-replace:winUTF8fix', 'cssmin','jshint']);
};
