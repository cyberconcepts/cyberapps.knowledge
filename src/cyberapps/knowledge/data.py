#
#  Copyright (c) 2015 Helmut Merz helmutm@cy55.de
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Classes for Knowledge and Skills Management.
"""

from zope.app.container.interfaces import INameChooser
from zope.component import adapts
from zope.interface import implements
from zope.traversing.api import getName

from cyberapps.knowledge.interfaces import IJobPosition, IQualification
from cyberapps.knowledge.interfaces import IJPDescription, IIPSkillsRequired
from cyberapps.knowledge.interfaces import IQualificationsRequired
from cyberapps.knowledge.interfaces import IQualificationsRecorded
from cyberapps.knowledge.interfaces import ISkillsRecorded
from cyberapps.knowledge.interfaces import IIPSkillsQuestionnaire
from cybertools.organize.interfaces import IPerson
from loops.common import AdapterBase, adapted, baseObject
from loops.concept import Concept
from loops.interfaces import IConcept
from loops.knowledge.survey.base import Questionnaire
from loops.organize.party import getPersonForUser
from loops.setup import addObject
from loops.table import DataTable
from loops.type import TypeInterfaceSourceList
from loops import util


TypeInterfaceSourceList.typeInterfaces += (
        IJobPosition, IJPDescription, IIPSkillsRequired, 
        IQualificationsRequired, IQualification,
        IQualificationsRecorded, ISkillsRecorded,
        IIPSkillsQuestionnaire)


class JobPosition(AdapterBase):

    implements(IJobPosition)

    def getPersons(self):
        result = [adapted(c) for c in self.context.getChildren()]
        return [p for p in result if IPerson.providedBy(p)]

    def getJPDescription(self):
        for c in self.context.getChildren():
            obj = adapted(c)
            if IJPDescription.providedBy(obj):
                return obj

    def createJPDescription(self):
        concepts = self.getLoopsRoot().getConceptManager()
        name = 'jpdesc.' + self.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['jpdescription']
        obj = addObject(concepts, Concept, name, type=type,
                        title='JP Description: ' + self.title)
        self.context.assignChild(obj)
        return adapted(obj)


    def getIPSkillsRequired(self):
        for c in self.context.getChildren():
            obj = adapted(c)
            if IIPSkillsRequired.providedBy(obj):
                return obj

    def createIPSkillsRequired(self):
        concepts = self.getLoopsRoot().getConceptManager()
        name = 'ipsreq.' + self.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['ipskillsrequired']
        obj = addObject(concepts, Concept, name, type=type,
                        title='IP Skills Req: ' + self.title)
        self.context.assignChild(obj)
        return adapted(obj)

    def getQualificationsRequired(self):
        for c in self.context.getChildren():
            obj = adapted(c)
            if IQualificationsRequired.providedBy(obj):
                return obj

    def createQualificationsRequired(self):
        concepts = self.getLoopsRoot().getConceptManager()
        name = 'qureq.' + self.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['qualificationsrequired']
        obj = addObject(concepts, Concept, name, type=type,
                        title='Qualifications Req: ' + self.title)
        self.context.assignChild(obj)
        return adapted(obj)


class JPDescription(AdapterBase):

    implements(IJPDescription)

    _contextAttributes = AdapterBase._contextAttributes + list(IJPDescription)


class IPSkillsRequired(AdapterBase):

    implements(IIPSkillsRequired)

    _contextAttributes = AdapterBase._contextAttributes + list(IIPSkillsRequired)


class QualificationsRequired(AdapterBase):

    implements(IQualificationsRequired)

    _contextAttributes = (AdapterBase._contextAttributes + 
                            list(IQualificationsRequired))


class Qualification(DataTable):

    implements(IQualification)

    _contextAttributes = AdapterBase._contextAttributes + list(IQualification)


class QualificationsRecorded(AdapterBase):

    implements(IQualificationsRecorded)

    _contextAttributes = (AdapterBase._contextAttributes + 
                            list(IQualificationsRecorded))


class SkillsRecorded(AdapterBase):

    implements(ISkillsRecorded)

    _contextAttributes = (AdapterBase._contextAttributes + 
                            list(ISkillsRecorded))


class IPSkillsQuestionnaire(Questionnaire):

    implements(IIPSkillsQuestionnaire)

    def getQuestionGroups(self, personId=None):
        if personId is None:
            person = getPersonForUser(self.context)
        else:
            person = util.getObjectForUid(personId)
        result = []
        required = self.getRequiredIPSkills(person)
        groups = super(IPSkillsQuestionnaire, self).getQuestionGroups()
        if not required:
            return groups
        for group in groups:
            skills = self.getIPSkillsForGroup(group)
            if skills:
                for skill in skills:
                    if skill in required:
                        result.append(group)
                        break
            else:
                result.append(group)
        return result

    def getIPSkillsForGroup(self, group):
        result = []
        for p in baseObject(group).getParents():
            if getName(p.conceptType) == 'ipskill':
                result.append(adapted(p))
        return result

    def getRequiredIPSkills(self, person):
        result = []
        for p in person.getParents():
            job = adapted(p)
            if IJobPosition.providedBy(job):
                requirements = job.getIPSkillsRequired().requirements
                for item in requirements.values():
                    if item.get('selected'):
                        result.append(util.getObjectForUid(item['uid']))
        return result
