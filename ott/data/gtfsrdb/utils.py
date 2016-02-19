

## NOTE: this won't work very well if we have a system running over time,
##       in that if we lose the connection to the databse, it won't reconnect...


gtfs_db = -1
def make_gtfs_db(url, schema):
    global gtfs_db
    if gtfs_db == -1:
        try:
            #import pdb; pdb.set_trace()
            from gtfsdb import Database
            kwargs = dict(
                schema=schema,
                url=url
            )
            gtfs_db = Database(**kwargs)
        except:
            print "no worries ... just letting you know there's no gtfsdb around, so I can't connect to that for more info..."
            gtfs_db = None

def get_gtfs_db(url, schema):
    make_gtfs_db(url, schema)
    return gtfs_db


def get_translation(string, lang):
    ''' get a specific translation from a TranslatedString
    '''

    # If we don't find the requested language, return this
    untranslated = None

    # single translation, return it
    if len(string.translation) == 1:
        return string.translation[0].text

    for t in string.translation:
        if t.language == lang:
            return t.text
        if t.language == None:
            untranslated = t.text
    return untranslated

getTrans = get_translation