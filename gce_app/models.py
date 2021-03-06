import os, uuid
from io import BytesIO
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from gce_app.functions import image_center_crop
########################################################################
#######  Modifications : 
##   1 - added OneToOneFields
##   2 - Ordered Tables
##   3 - Added Validators
##   4 - Changed Fields Labels
##   5 - Replaced Relation Tables with ManyToManyFields
########################################################################

## FUNCTIONS
def copies_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    current_annee = AnneeUniv.objects.all().order_by('-id')[0].annee_univ
    path = os.path.join('copies', current_annee)
    path = os.path.join(path, instance.id_module.id_specialite.id_parcours.id_filiere.id_domaine.nom)
    path = os.path.join(path, instance.id_module.id_specialite.id_parcours.nom)
    path = os.path.join(path, instance.id_module.titre_module)
    return os.path.join(path, filename)

def corrections_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    current_annee = AnneeUniv.objects.all().order_by('-id')[0].annee_univ
    path = os.path.join('corrections', current_annee)
    path = os.path.join(path, instance.id_correction.id_module.id_specialite.id_parcours.id_filiere.id_domaine.nom)
    path = os.path.join(path, instance.id_correction.id_module.id_specialite.id_parcours.nom)
    path = os.path.join(path, instance.id_correction.id_module.titre_module)
    return os.path.join(path, filename)

def avatars_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatars', filename)


## MODELS
class Utilisateur(models.Model):
    user_choices = (('etud','Etudiant'),('ensg','Enseignant'),('tech','Technicien'),('chef','Chef Departement'))
    type_utilisateur = models.CharField(db_column='type_Utilisateur', max_length=255, null=True, choices = user_choices)
    id_utilisateur = models.CharField(db_column='id_Utilisateur', primary_key=True, max_length=100, unique=True, blank=True, editable=False)
    avatar_utilisateur = models.FileField(db_column='Avatar', default = 'default/default_avatar.png', upload_to = avatars_file_path, max_length = 10000)
    info_utilisateur = models.OneToOneField(User,models.CASCADE)

    def save(self,*args, **kwargs):
        # creating user id
        if self.id_utilisateur == '':
            self.id_utilisateur = self.type_utilisateur + str(self.info_utilisateur.id)
        # cropping avatar to a square
        if self.avatar_utilisateur != 'default/default_avatar.png': # checking that this is not a user creation
            cropped_user_img = image_center_crop(self.avatar_utilisateur)
            cropped_user_img_io = BytesIO()
            cropped_user_img.save(cropped_user_img_io, format='JPEG')
            cropped_user_img_name = self.avatar_utilisateur.name
            self.avatar_utilisateur.delete(save=False)
            self.avatar_utilisateur.save(cropped_user_img_name,content=ContentFile(cropped_user_img_io.getvalue()),save=False)

        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'Utilisateur'


class Notification(models.Model):
    sujet_notification = models.CharField(db_column='sujet_Notification', max_length=100, blank=True, null=True)
    description_notification = models.CharField(db_column='description_Notification', max_length=250, blank=True, null=True)
    vue_notification = models.BooleanField(db_column='vue_Notification',default = False)
    date_notification = models.DateField(db_column='date_Notification', blank=True, null=True)
    heure_notification = models.TimeField(db_column='heure_Notification', blank=True, null=True)
    icon_notification = models.CharField(db_column='IconPath', blank=True, null=True,max_length=1000)
    id_utilisateur = models.ForeignKey('Utilisateur', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)
    
    class Meta:
        db_table = 'Notification'


class ChefDepartement(models.Model):
    id_chef_departement = models.OneToOneField('Utilisateur', models.CASCADE, db_column='id_Utilisateur', primary_key=True)
    
    class Meta:
        db_table = 'Chef_Departement'


class Universite(models.Model):
    nom = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        db_table = 'Universite'


class Faculte(models.Model):
    nom = models.CharField(max_length=1000, blank=True, null=True)
    id_universite = models.ForeignKey('Universite', models.CASCADE, db_column='id_Universite', blank=True, null=True)

    class Meta:
        db_table = 'Faculte'


class Domaine(models.Model):
    nom = models.CharField(max_length=1000)
    id_faculte = models.ForeignKey('Faculte', models.CASCADE, db_column='id_Faculte', blank=True, null=True)

    class Meta:
        db_table = 'Domaine'


class Filiere(models.Model):
    nom = models.CharField(max_length=1000)
    id_domaine = models.ForeignKey(Domaine, models.CASCADE, db_column='id_Domaine')
    id_chef_departement = models.ForeignKey('ChefDepartement', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)

    class Meta:
        db_table = 'Filiere'


class Parcours(models.Model):
    nom = models.CharField(max_length=100)
    id_filiere = models.ForeignKey('Filiere', models.CASCADE, db_column='id_Filiere')

    class Meta:
        db_table = 'Parcours'


class Specialite(models.Model):
    nom = models.CharField(max_length=1000)
    id_parcours = models.ForeignKey('Parcours', models.CASCADE, db_column='id_Parcours')

    class Meta:
        db_table = 'Specialite'


class Section(models.Model):
    numero = models.IntegerField()
    id_specialite = models.ForeignKey('Specialite', models.CASCADE, db_column='id_Specialite')

    class Meta:
        db_table = 'Section'


class Groupe(models.Model):
    numero = models.IntegerField()
    id_section = models.ForeignKey('Section', models.CASCADE, db_column='id_Section')

    class Meta:
        db_table = 'Groupe'


class Technicien(models.Model):
    id_technicien = models.OneToOneField('Utilisateur', models.CASCADE, db_column='id_Utilisateur', primary_key=True)
    id_faculte = models.ForeignKey('Faculte', models.CASCADE, db_column='id_Faculte', unique=False, null=True)

    class Meta:
        db_table = 'Technicien'


class Enseignant(models.Model):
    id_enseignant = models.OneToOneField('Utilisateur', models.CASCADE, db_column='id_Utilisateur', primary_key=True)
    filieres = models.ManyToManyField('Filiere', blank = True)
    modules = models.ManyToManyField('Module', blank = True)
    
    class Meta:
        db_table = 'Enseignant'


class Etudiant(models.Model):
    id_etudiant = models.OneToOneField('Utilisateur', models.CASCADE, db_column='id_Utilisateur', primary_key=True)
    id_groupe = models.ForeignKey('Groupe', models.CASCADE, db_column='id_Groupe')
    
    class Meta:
        db_table = 'Etudiant'


class Module(models.Model):
    titre_module = models.CharField(db_column='titre_Module', max_length=1000, blank=True, null=True, unique=True)
    finsaisie_module = models.BooleanField(db_column='FinSaisie_Module', blank=True, default=False)
    id_specialite = models.ForeignKey('Specialite', models.CASCADE , blank = True, null = True, unique = False)

    class Meta:
        db_table = 'Module'


class Annonce(models.Model):
    sujet_annonce = models.CharField(db_column='sujet_Annonce', max_length=500, blank=True, null=True)
    description_annonce = models.CharField(db_column='description_Annonce', max_length=10000, blank=True, null=True)
    date_annonce = models.DateField(db_column='date_Annonce', blank=True, null=True)
    heure_annonce = models.TimeField(db_column='heure_Annonce', blank=True, null=True)
    afficher_annonce = models.BooleanField(db_column='afficher_Annonce', default=False)
    id_module = models.ManyToManyField('Module', blank = True)
    id_parcours = models.ManyToManyField('Parcours', blank = True)
    id_filiere = models.ForeignKey('Filiere', models.CASCADE, db_column='id_Filiere', blank=True, null=True)

    class Meta:
        db_table = 'Annonce'


class Copie(models.Model):
    rectifier = models.BooleanField(db_column='Rectifier', default=False)
    afficher_copie = models.BooleanField(db_column='afficher_Copie', default=False)
    date_affichage = models.DateField(db_column='date_Affichage', blank=True, null=True)
    modifiable = models.BooleanField(db_column='Modifiable', default=True)
    id_module = models.ForeignKey('Module', models.CASCADE, db_column='id_Module', blank=True, null=True)
    id_etudiant = models.ForeignKey('Etudiant', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)
    annee_copie = models.ForeignKey('AnneeUniv', models.SET_NULL, db_column='annee_Copie', blank=True, null=True)

    class Meta:
        db_table = 'Copie'


class VersionCopie(models.Model):
    numero_version = models.IntegerField(db_column='numero_Version', blank=True, null=True)
    note_version = models.FloatField(db_column='note_Version', blank=True, null=True)
    id_copie = models.ForeignKey('Copie', models.CASCADE , db_column='id_Copie', blank=True, null=True)
    temp_version =  models.BooleanField(db_column='temp_Version', default=False)

    class Meta:
        db_table = 'VersionCopie'


class FichierCopie(models.Model):
    emplacement_fichier = models.FileField(db_column='emplacement_Fichier', blank=True, null=True, upload_to = copies_file_path, max_length = 10000)
    id_version = models.ForeignKey('VersionCopie', models.SET_NULL, db_column='id_Version', blank=True, null=True)
    id_module = models.ForeignKey('Module', models.CASCADE, db_column='id_Module', blank=True, null=True)

    class Meta:
        db_table = 'FichierCopie'


class Correction(models.Model):
    id_module = models.ForeignKey('Module', models.CASCADE, db_column='id_Module', blank=True, null=True)
    id_enseignant = models.ForeignKey('Enseignant', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)
    annee_correction = models.ForeignKey('AnneeUniv', models.SET_NULL, db_column='annee_Correction', blank=True, null=True)
    
    class Meta:
        db_table = 'Correction'


class FichierCorrection(models.Model):
    emplacement_fichier = models.FileField(db_column='emplacement_Fichier', blank=True, null=True, upload_to=corrections_file_path, max_length = 10000)
    id_correction = models.ForeignKey('Correction', models.CASCADE, db_column='id_Correction', blank=True, null=True)

    class Meta:
        db_table = 'FichierCorrection'


class Reclamation(models.Model):
    sujet_reclamation = models.CharField(db_column='Sujet_Reclamation', max_length=500, blank=True, null=True)
    description_reclamation = models.CharField(db_column='Description_Reclamation', max_length=10000, blank=True, null=True)
    id_etudiant = models.ForeignKey('Etudiant', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)
    id_module = models.ForeignKey('Module', models.CASCADE, db_column='id_Module', blank=True, null=True)
    annee_reclamation =  models.ForeignKey('AnneeUniv', models.SET_NULL, db_column='annee_Reclamation', blank=True, null=True)
    regler_reclamation = models.BooleanField(db_column='regler_Reclamation', default=False)
    approuver_reclamation = models.BooleanField(db_column='approuver_Reclamation', default=False)
    old_files = models.ManyToManyField("FichierCopie", related_name="old_files", blank = True)
    new_files = models.ManyToManyField("FichierCopie", related_name="new_files", blank = True)
    
    class Meta:
        db_table = 'Reclamation'


class Consultation(models.Model):
    sale_consultation = models.CharField(db_column='sale_Consultation', max_length=250, blank=True, null=True)
    date_consultation = models.DateField(db_column='date_Consultation', blank=True, null=True)
    heure_consultation = models.TimeField(db_column='heure_Consultation', blank=True, null=True)
    afficher_consultation = models.BooleanField(db_column='afficher_Consultation', default=False)
    approve_consultation = models.BooleanField(db_column='approve_Consultation', default=False)
    id_enseignant = models.ForeignKey('Enseignant', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)
    id_module = models.ForeignKey('Module', models.CASCADE, db_column='id_Module', blank=True, null=True)

    class Meta:
        db_table = 'Consultation'


class AnneeUniv(models.Model):
    annee_univ = models.CharField(db_column='annee_Univ', max_length=500, null=True)
    active = models.BooleanField(db_column='active_Univ', default = False)
    
    class Meta:
        db_table = 'anneeUniv'


class Affichage(models.Model):
    id_module = models.ForeignKey('Module', models.CASCADE, db_column='id_Module_affichage', blank=True, null=True)
    afficher = models.BooleanField(db_column='afficher_affichage', default = False)
    copies = models.ManyToManyField('VersionCopie', blank = True)
    
    class Meta:
        db_table = 'Affichage'


# class DiscussionAdministrative(models.Model):
#     id_chef_departement = models.ForeignKey('ChefDepartement', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)
#     id_enseignant = models.ForeignKey('Enseignant', models.CASCADE, db_column='id_Utilisateur_1', blank=True, null=True)

#     class Meta:
#         db_table = 'Discussion_Administrative'


# class DiscussionReclamation(models.Model):
#     id_reclamation = models.ForeignKey('Reclamation', models.CASCADE, db_column='id_Reclamation', blank=True, null=True)
#     id_enseignant = models.ForeignKey('Enseignant', models.CASCADE, db_column='id_Utilisateur', blank=True, null=True)

#     class Meta:
#         db_table = 'Discussion_Reclamation'


# class MessagesAdministrative(models.Model):
#     contenu_message = models.CharField(db_column='contenu_Message', max_length=10000, blank=True, null=True)
#     date_message = models.DateField(db_column='date_Message', blank=True, null=True)
#     heure_message = models.TimeField(db_column='heure_Message', blank=True, null=True)
#     id_emetteur = models.CharField(db_column='id_Emetteur', max_length=100, blank=True, null=True)
#     id_recepteur = models.CharField(db_column='id_Recepteur', max_length=100, blank=True, null=True)
#     id_discussion = models.ForeignKey('DiscussionAdministrative', models.CASCADE, db_column='id_Discussion', blank=True, null=True)

#     class Meta:
#         db_table = 'Messages_Administrative'


# class MessagesReclamation(models.Model):
#     contenu_message = models.CharField(db_column='contenu_Message', max_length=10000, blank=True, null=True)
#     date_message = models.DateField(db_column='date_Message', blank=True, null=True)
#     heure_message = models.TimeField(db_column='heure_Message', blank=True, null=True)
#     id_emetteur = models.CharField(db_column='id_Emetteur', max_length=100, blank=True, null=True)
#     id_recepteur = models.CharField(db_column='id_Recepteur', max_length=100, blank=True, null=True)
#     id_discussion = models.ForeignKey('DiscussionReclamation', models.CASCADE, db_column='id_Discussion', blank=True, null=True)

#     class Meta:
#         db_table = 'Messages_Reclamation'