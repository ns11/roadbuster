// #####################################################################################################################
// #IMPORTS#
var gulp = require('gulp');
var gutil = require('gulp-util');
var plumber = require('gulp-plumber');
var fs = require('fs');
var autoprefixer = require('autoprefixer');
var postcss = require('gulp-postcss');
var gulpif = require('gulp-if');
var iconfont = require('gulp-iconfont');
var iconfontCss = require('gulp-iconfont-css');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var minifyCss = require('gulp-clean-css');
var eslint = require('gulp-eslint');
var webpack = require('webpack');
var KarmaServer = require('karma').Server;
var integrationTests = require('djangocms-casper-helpers/gulp');

var argv = require('minimist')(process.argv.slice(2)); // eslint-disable-line

// #####################################################################################################################
// #SETTINGS#
var options = {
    debug: argv.debug
};
var PROJECT_ROOT = __dirname + '/cms/static/cms';
var PROJECT_PATH = {
    js: PROJECT_ROOT + '/js',
    sass: PROJECT_ROOT + '/sass',
    css: PROJECT_ROOT + '/css',
    icons: PROJECT_ROOT + '/fonts',
    tests: __dirname + '/cms/tests/frontend'
};

var PROJECT_PATTERNS = {
    js: [
        PROJECT_PATH.js + '/modules/*.js',
        PROJECT_PATH.js + '/widgets/*.js',
        PROJECT_PATH.js + '/*.js',
        PROJECT_PATH.js + '/gulpfile.js',
        PROJECT_PATH.tests + '/**/*.js',
        '!' + PROJECT_PATH.tests + '/unit/helpers/**/*.js',
        '!' + PROJECT_PATH.tests + '/coverage/**/*.js',
        '!' + PROJECT_PATH.js + '/modules/jquery.*.js',
        '!' + PROJECT_PATH.js + '/dist/*.js'
    ],
    sass: [PROJECT_PATH.sass + '/**/*.{scss,sass}'],
    icons: [PROJECT_PATH.icons + '/src/*.svg']
};

var INTEGRATION_TESTS = [
    [
        'loginAdmin', // WORKS
        'toolbar', // WORKS
        // 'addFirstPage', // broken
        // 'wizard',  FIXME broken wizard step 2 form in Django >= 2.0
        // 'editMode', // broken
        'sideframe', // WORKS
        'createContent',
        'users', // WORKS
        'addNewUser', // WORKS
        // 'newPage', // after removing resolve endpoint the cms no longer redirects you to new page
        // 'pageControl', // broken
        'modal', // WORKS
        // 'permissions', // broken
        // 'logout', // FIXME fails because the only page created in the project doesn't seem to be "live", shows 404
        // logged out user
        // 'clipboard', // fails because the urls returned from copy endpoint are wrong
        'link-plugin-content-mode', // WORKS
        'add-multiple-plugins' // WORKS
    ],
    [
        // 'pageTypes', // FIXME fails on adding TextPlugin mid tree
        // 'switchLanguage', // FIXME fails because EmptyTitle doesn't have rescan_placeholders
        'editContent', // FIXME broken cause of text plugin
        // 'editContentTools', // FIXME fails when pasting with a weird error. looks ckeditor related
        // 'publish', // broken
        // 'loginToolbar', // fails since page is never published
        'changeSettings', // WORKS
        // 'toolbar-login-apphooks', // broken
        // 'permissions-enabled', // permissions were moved into advanced settings
        // {
        //     serverArgs: '--CMS_PERMISSION=False --CMS_TOOLBAR_URL__EDIT_ON=test-edit',
        //     file: 'copy-from-language'
        // },
        // {
        //     serverArgs: '--CMS_PERMISSION=False --CMS_TOOLBAR_URL__EDIT_ON=test-edit',
        //     file: 'pagetree-no-permission'
        // },
        // {
        //     serverArgs: '--CMS_PERMISSION=False --CMS_TOOLBAR_URL__EDIT_ON=test-edit',
        //     file: 'permissions-disabled' // permissions were moved into advanced settings
        // }
    ],
    [
        'pagetree',
        'pagetree-drag-n-drop-copy',
        'disableToolbar', // WORKS
        // 'dragndrop', // FIXME broken cause of text editor
        'copy-apphook-page' // WORKS
        // 'revertLive', // disabled since functionality is no longer there
        // 'narrowScreen',
        // 'nonadmin'
    ]
];

var CMS_VERSION = fs.readFileSync('cms/__init__.py', { encoding: 'utf-8' }).match(/__version__ = '(.*?)'/)[1];

// #####################################################################################################################
// #TASKS#
gulp.task('sass', function() {
    gulp
        .src(PROJECT_PATTERNS.sass)
        .pipe(gulpif(options.debug, sourcemaps.init()))
        .pipe(sass())
        .on('error', function(error) {
            gutil.log(gutil.colors.red('Error (' + error.plugin + '): ' + error.messageFormatted));
        })
        .pipe(
            postcss([
                autoprefixer({
                    cascade: false
                })
            ])
        )
        .pipe(
            minifyCss({
                rebase: false
            })
        )
        .pipe(gulpif(options.debug, sourcemaps.write()))
        .pipe(gulp.dest(PROJECT_PATH.css + '/' + CMS_VERSION + '/'));
});

gulp.task('icons', function() {
    gulp
        .src(PROJECT_PATTERNS.icons)
        .pipe(
            iconfontCss({
                fontName: 'django-cms-iconfont',
                fontPath: '../../fonts/' + CMS_VERSION + '/',
                path: PROJECT_PATH.sass + '/libs/_iconfont.scss',
                targetPath: '../../sass/components/_iconography.scss'
            })
        )
        .pipe(
            iconfont({
                fontName: 'django-cms-iconfont',
                normalize: true
            })
        )
        .on('glyphs', function(glyphs, opts) {
            gutil.log.bind(glyphs, opts);
        })
        .pipe(gulp.dest(PROJECT_PATH.icons + '/' + CMS_VERSION + '/'));
});

gulp.task('lint', ['lint:javascript']);
gulp.task('lint:javascript', function() {
    // DOCS: http://eslint.org
    return gulp
        .src(PROJECT_PATTERNS.js)
        .pipe(gulpif(!process.env.CI, plumber()))
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failAfterError())
        .pipe(gulpif(!process.env.CI, plumber.stop()));
});

gulp.task('tests', ['tests:unit', 'tests:integration']);

// gulp tests:unit --tests=cms.base,cms.modal
gulp.task('tests:unit', function(done) {
    var server = new KarmaServer(
        {
            configFile: PROJECT_PATH.tests + '/karma.conf.js',
            singleRun: true
        },
        done
    );

    server.start();
});

gulp.task('tests:unit:watch', function() {
    var server = new KarmaServer({
        configFile: PROJECT_PATH.tests + '/karma.conf.js'
    });

    server.start();
});

// gulp tests:integration [--clean] [--screenshots] [--tests=loginAdmin,toolbar]
gulp.task(
    'tests:integration',
    integrationTests({
        tests: INTEGRATION_TESTS,
        pathToTests: PROJECT_PATH.tests,
        argv: argv,
        dbPath: 'testdb.sqlite',
        serverCommand: 'testserver.py',
        logger: gutil.log.bind(gutil),
        waitForMigrations: 5 // seconds
    })
);

var webpackBundle = function(opts) {
    var webpackOptions = opts || {};

    webpackOptions.PROJECT_PATH = PROJECT_PATH;
    webpackOptions.debug = options.debug;
    webpackOptions.CMS_VERSION = CMS_VERSION;

    return function(done) {
        var config = require('./webpack.config')(webpackOptions);

        webpack(config, function(err, stats) {
            if (err) {
                throw new gutil.PluginError('webpack', err);
            }
            gutil.log('[webpack]', stats.toString({ maxModules: Infinity, colors: true, optimizationBailout: true }));
            if (typeof done !== 'undefined' && (!opts || !opts.watch)) {
                done();
            }
        });
    };
};

gulp.task('bundle:watch', webpackBundle({ watch: true }));
gulp.task('bundle', webpackBundle());

gulp.task('watch', function() {
    gulp.start('bundle:watch');
    gulp.watch(PROJECT_PATTERNS.sass, ['sass']);
    gulp.watch(PROJECT_PATTERNS.js, ['lint']);
});

gulp.task('default', ['sass', 'lint', 'watch']);
