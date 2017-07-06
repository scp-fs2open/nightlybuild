<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>FSO Build Runner</title>
    <meta name="description" content="The SCP Build Runner for FSO">
    <meta name="author" content="Cliff 'chief1983' Gordon">
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script type="text/javascript" src="js/fsobuild.js"></script>
    <link rel="stylesheet" type="text/css" href="styles/main.css" />
</head>
<body>
    <h2>FSO Build Runner</h2>
    <div id="runbuild">
        <form action="<?=$_SERVER['PHP_SELF']?>" method="POST">
            <table>
                <tr>
                    <td><label for="version">Version (The version to mark this release as)</label></td>
                    <td><input type="text" id="version" name="version" /></td>
                </tr>
                <tr>
                    <td><label for="tag_name">Tag Name (Overrides the tag name to check.
                    This skips the tag and push phase of the script)</label></td>
                    <td><input type="text" id="tag_name" name="tag_name" /></td>
                </tr>
                <tr>
                    <td colspan="2"><input type="submit" name="submit_run" id="submit_run" value="Run" /></td>
                </tr>
            </table>
        </form>
    </div>
    <h4>Recent Builds</h4>
    <div id="buildstatus">
        <table>
            <thead>
                <tr>
                    <th class="tableindex">Index</th>
                <?php foreach ($fields as $field => $label) : ?>
                    <th class="<?=$field?>"><?=$label?></th>
                <?php endforeach; ?>
                </tr>
            </thead>
            <tbody>
            <?php foreach ($builds as $tableindex => $build) : ?>
                <tr>
                    <td class="tableindex"><a
                        href="<?=$_SERVER['PHP_SELF']?>?buildid=<?=$build['id']?>"><?=$tableindex+1?></a></td>
                <?php foreach ($build as $fieldindex => $field) : ?>
                    <td class="<?=$fieldindex?>"><?=$field?></td>
                <?php endforeach; ?>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <a href="<?=$_SERVER['PHP_SELF']?>?logout=1">Logout</a>
</body>
</html>
