# estela CLI Quickstart

## Getting Help
To see all available commands, run:

```bash
$ estela
```

For help on a specific command, append the `-h` or `--help` flag, e.g.:

```bash
$ estela create job --help
```

## Basic Usage
To start using the estela CLI with estela, first, you need to log in:

```bash
$ estela login
```

estela CLI will prompt for your credentials. You should see the following output:

```bash
$ estela login
Host [http://localhost]:
Username: admin
Password:
Successful login. API Token stored in ~/.estela.yaml.
```

This will save your estela API key to the file `~/.estela.yaml`, and it is
needed to access projects associated with your account.  

<blockquote style="background-color: #ffffcc; border-left: 6px solid #ffee99; padding: 10px;">
  If you have installed estela locally run the following command to obtain the host of the estela api:

```bash
$ kubectl get service estela-django-api-service -o custom-columns=':status.loadBalancer.ingress[0].ip' \
| tr -d '[:space:]' \
| paste -d "/" <(echo "http:/") - 
```

  To make this command work, you should run `minikube tunnel`.

</blockquote>

<blockquote class="note">
<b>Note:</b> You can use the superuser credentials that you set with `make createsuperuser` to log in.
</blockquote>

### Creating a project

In estela, a project is an identifier that groups spiders. It is linked to the
Docker image of a Scrapy project. A project's spiders are extracted automatically from the Scrapy
project.

To create a project, use the command `estela create project <project_name>`, which on success,
should return a message like the following:

```bash
$ estela create project proj_test
project/proj_test created.
Hint: Run 'estela init 23ea584d-f39c-85bd-74c1-9b725ffcab1d7' to activate this project
```

With this, we have created a project in estela. Note the hint in the last
line of the output. It shows us the ID of the project we have just created in
UUID format.

A project cannot run spiders if it is not linked to the Docker image of a Scrapy Project.

### Linking an Scrapy project

To link a project, navigate to a Scrapy project with the following structure:

```
scrapy_project_dir
----scrapy_project/
    ----spiders/
    ----downloader.py
    ----items.py
    ----middlewares.py
    ----pipelines.py
    ----settings.py
----scrapy.cfg
----requirements.txt
```

Then, run the suggested command to activate the project:
```bash
$ estela init 23ea584d-f39c-85bd-74c1-9b725ffcab1d7
```

### Linking a Requests Project

If you are using a Requests project instead of a Scrapy project, you can link it to Estela by following these steps:

1. Ensure you have created a Requests project using Estela Requests. Refer to the [Estela Requests documentation](https://github.com/bitmakerla/estela-requests/tree/main#basic-usage) for instructions on creating a project.

2. Navigate to the root directory of your Requests project.

3. Run the following command to activate the project, replacing `23ea584d-f39c-85bd-74c1-9b725ffcab1d7` with the ID of your Estela project:

   ```bash
   $ estela init 23ea584d-f39c-85bd-74c1-9b725ffcab1d7 -p requests
   ```

   This command links your Requests project to the corresponding Estela project, allowing you to utilize Estela's features for managing and running your project.
   
   <blockquote style="background-color: #ffffcc; border-left: 6px solid #ffee99; padding: 10px;">
   In order to be discoverable, **spiders should reside in the project's root directory**. However, please note that this will be enhanced in the future to provide greater flexibility.
   </blockquote>


This will create the files `.estela/Dockerfile-estela.yaml` and `estela.yaml`
in your project directory. `estela.yaml` contains the project ID and the Docker
image's name in the AWS registry. This file will also
[configure your project](configuration.md), allowing you to
change the Python version, requirements file path, and files to ignore when
deploying (like your virtual environment).

Alternatively, suppose you created the project via the web interface.
In that case, you can directly use the `estela init <project_id>` command with
the project ID that you can find on the project detail page.

We have successfully linked our estela project with our Scrapy project.

### Deploying a project
This is a simple and essential step. Once the estela and Scrapy projects are linked,
we will proceed to build the Docker image and upload it to the AWS registry. This whole process
will be done automatically and scheduled by the API with
the command:

```bash
$ estela deploy
```

You must run this command in the root directory of your Scrapy project (where the `estela.yaml` file is).
This will verify whether any changes to the Dockerfile are needed, caused by making changes in the `estela.yaml` file.
Then, it will zip our Scrapy project and upload it to the API, which will take care of the rest
of the process.

```bash
$ estela deploy
.estela/Dockerfile-estela not changes to update.
✅ Project uploaded successfully. Deploy 19 underway.
```

After the deployment is complete, you can see the spiders in your project with
```bash
$ estela list spider
NAME    SID
quotes  101
```

And you can create jobs and cronjobs using the estela CLI with `estela create job <SID>`
and `estela create cronjob <CRONTAB_SCHEDULE> <SID>`.

You can see the list of jobs that have run or are running for a spider with:
```bash
$ estela list job <SID>
JID    STATUS     TAGS          ARGS    ENV VARS    CREATED
1943   Completed                                    2022-03-18 14:40
1850   Completed                                    2022-03-10 14:14
```

You can get the scraped items even while the spider is running by supplying the job ID:
```bash
$ estela data <JID> <SID>
✅ Data retrieved succesfully.
✅ Data saved succesfully.
```

This will save the data in a directory `project_data/` in JSON format. You can also retrieve
the data in CSV format by adding the option `--format csv`.