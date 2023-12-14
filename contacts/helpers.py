def getEmailFromContactId(contactId):
    try:
        contact = Contact.objects.get(id=contactId)
        return contact.email
    except Contact.DoesNotExist:
        return None
    
def getFirstNameFromContactId(contactId):
    try:
        contact = Contact.objects.get(id=contactId)
        return contact.first_name
    except Contact.DoesNotExist:
        return None
    
def getLastNameFromContactId(contactId):
    try:
        contact = Contact.objects.get(id=contactId)
        return contact.last_name
    except Contact.DoesNotExist:
        return None

def getCompanyNameFromContactId(contactId):
    try:
        contact = Contact.objects.get(id=contactId)
        return contact.company
    except Contact.DoesNotExist:
        return None
    
def getTypeFromContactId(contactId):
    try:
        contact = Contact.objects.get(id=contactId)
        return contact.type
    except Contact.DoesNotExist:
        return None

def getTitleFromContactId(contactId):
    try:
        contact = Contact.objects.get(id=contactId)
        return contact.title
    except Contact.DoesNotExist:
        return None