from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from subprocess import call
from webpages import create_standard_webpage
import codecs
import time

def build_folders(source, destination, standards, root):
    print "Building register..."

    source_fs = OSFS(source)

    # iterate over all standards in source directory
    for standard in standards:
        print "Processing %s ... " % standard['id']
        standard_fs = source_fs.opendir(standard['id'])

        # list all sub standards of a standard
        artifacts = standard_fs.listdir(dirs_only=True)
        if '.git' in artifacts: artifacts.remove(".git")

        for artifact in artifacts:
            # check whether artifact folder exists in destination 
            if root.exists('%s/%s' % (destination, artifact)) == False:
                root.makedir('%s/%s' % (destination, artifact))
                
            # copy standard folders from source to destination in desired structure
            root.copydir('%s/%s/%s' % (source, standard['id'], artifact),  '%s/%s/%s' % (destination, artifact, standard['id']))

        # create standard HTML page
        html = create_standard_webpage(standard, artifacts)

        # check whether standard folder exists in register root
        if root.exists('%s/%s' % (destination, standard['id'])) == False:
            root.makedir('%s/%s' % (destination, standard['id']))
        
        # write standard HTML page to register/standard/index.html
        with codecs.open('%s/%s/index.html' % (destination, standard['id']), 'w', encoding='utf8') as f:
            f.write(html)

def fetch_repos(root, destination, repos, source):
    print "Fetching repositories..."

    for repo in repos:
        print "Cloning %s in repos/%s" % (repo['url'], repo['id'])
        # explicitely create dir as implicit cration fails on server
        root.makedir('%s/%s' % (destination, repo['id']))
        call('git clone %s %s/%s' % (repo['url'], source, repo['id']), shell=True)

    #TODO: git pull additions into existing repos, clone new ones

def create_staging(destination):
	print 'Copying register to staging...'

	call('rm -rf ../register/staging', shell=True)

	call('mv %s ../register/staging' % destination, shell=True)
	# root.copydir(destination, '../register/staging')
	# root.removedir(destination, force=True)
	
	# call('rm -rf %s' % source, shell=True)
	call('chmod -R a+rx ../register/staging', shell=True)
	# root.removedir(source, force=True)

def put_in_production():
	print "!! === !!"
	print "Putting staging in production"
	# backup current register

	print "Backing up register..."
	call('cp -r ../register ../backups/%s' % time.strftime('%Y-%m-%d'))

	#copy staging to parent dir
	print "Preparing staging for launch..."
	call('cp -r ../register/staging ../register-staging')
	call('cp -r ../register/staging ../register-staging2')

	#rename old register to temp name
	print "Launching staging into production..."
	call('mv ../register ../register-old')
	
	#rename staging to new register
	call('mv ../register-staging ../register')
	# call('mkdir ../register/r')
	call('cp -r web/assets ../register/r')
	print "Staging launched!"
	
	# delelete old register
	print "Removing old register..."
	call('rm -rf ../register-old')

	# move current staging to new register
	print "Moving current staging to new production..."
	call('mv ../register-staging2 ../register/staging')