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
Definition of classes for viewing reporting data in cyberapps.knowledge.
"""

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy

from loops.common import adapted
from loops import util
from cyberapps.knowledge.browser.qualification import \
        JobPositionsOverview, PositionView, JPDescForm
from cyberapps.knowledge.browser.qualification import template as baseTemplate
                                    

template = ViewPageTemplateFile('report_macros.pt')


class ReportBaseView(object):

    template = template
    templateName = 'knowledge.report'
    baseTemplate = baseTemplate


class JobsListing(ReportBaseView, JobPositionsOverview):

    macroName = 'jobs'

    def update(self):
        instUid = self.request.form.get('select_institution')
        if instUid:
            return self.setInstitution(instUid)


class JobDescription(ReportBaseView, JPDescForm):

    macroName = 'jobdescription'

    @Lazy
    def breadcrumbsParent(self):
        for p in self.context.conceptType.getParents([self.queryTargetPredicate]):
            pass
        return self.nodeView.getViewForTarget(p)

    def getData(self):
        self.setupController()
        self.registerDojoSlider()
        result = dict(header={}, administrative=[], workdesc=[], 
                      qualifications=[], ipskills=[])
        data = dict(header={}, administrative={}, workdesc={}, 
                    qualifications={}, ipskills={})
        # load data
        jp = adapted(self.target)
        jpDesc = jp.getJPDescription()
        if jpDesc is not None:
            if jpDesc.administrativeData:
                data['administrative'] = jpDesc.administrativeData
            if jpDesc.workDescription:
                data['workdesc'] = jpDesc.workDescription
            if jpDesc.header:
                data['header'] = result['header'] = jpDesc.header
        qureq = adapted(self.target).getQualificationsRequired()
        if qureq is not None:
            data['qualifications'] = qureq.requirements
        skillsreq = adapted(self.target).getIPSkillsRequired()
        if skillsreq is not None:
            data['ipskills'] = skillsreq.requirements
        # administrative data
        adminDT = adapted(self.conceptManager['jpdesc_administrative'])
        for row in adminDT.data.values():
            key, label, desc, optional = row
            dataRow = data['administrative'].get(key) or {}
            if dataRow.get('inactive'):
                continue
            result['administrative'].append(
                dict(key=key, label=label, desc=desc, optional=bool(optional),
                     text=dataRow.get('text') or u''))
        # work description
        workdescDT = adapted(self.conceptManager['jpdesc_workdesc'])
        for row in workdescDT.data.values():
            key, label, desc, optional = row
            dataRow = data['workdesc'].get(key) or {}
            if dataRow.get('inactive'):
                continue
            result['workdesc'].append(
                dict(key=key, label=label, desc=desc, optional=bool(optional),
                     text=dataRow.get('text') or (5 * [u''])))
        # qualifications
        qualifications = self.conceptManager['qualifications']
        for obj in qualifications.getChildren([self.defaultPredicate]):
            uid = util.getUidForObject(obj)
            dataRow = data['qualifications'].get(uid) or {}
            item = dict(key=uid, label=obj.title, 
                        desc=obj.description, schema=[],
                        value=dataRow.get('value') or (3 * [u'']),
                        req=dataRow.get('req') or (3 * [u'0']))
            for row in adapted(obj).data.values():
                key = row[0]
                value = dataRow.get('qu_' + key) or (3 * [u''])
                item['schema'].append(dict(                            
                            key=key, label=row[1], 
                            level=row[2], type=row[4], 
                            value=value))
            result['qualifications'].append(item)
        # ipskills
        ipskills = self.conceptManager['ipskills']
        for parent in ipskills.getChildren([self.defaultPredicate]):
            uid = util.getUidForObject(parent)
            item = dict(uid=uid, label=parent.title, 
                        description=parent.description, skills=[])
            for child in parent.getChildren([self.defaultPredicate]):
                uid = util.getUidForObject(child)
                row = data['ipskills'].get(uid) or {}
                if row.get('selected'):
                    item['skills'].append(
                        dict(uid=uid, label=child.title,
                             description=child.description,
                             expected=row.get('expected') or 0))
            result['ipskills'].append(item)
        return result
