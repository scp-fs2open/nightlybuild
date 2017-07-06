<?php

/**
 * Simple class for handling things common to the build output table
 */
class BuildTable
{
    public static $fields = array(
        'id' => 'ID',
        'version' => 'Version',
        'tag_name' => 'Tag Name',
        // 'config' => 'Config',
        'pid' => 'pid',
        'started' => 'Started',
        'completed' => 'Completed',
        'status' => 'Status',
    );

    /**
     * Queries a database for all builds
     * @param  resource $db PDO connection
     * @return array        Array of builds
     */
    public static function getBuilds($db)
    {
        return $db->query("SELECT ".implode(', ', array_keys(self::$fields))." FROM jobs")->fetchAll(PDO::FETCH_ASSOC);
    }
}
