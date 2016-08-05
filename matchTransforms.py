
Skip to content
This repository

    Pull requests
    Issues
    Gist

    @illmillrig

1
0

    0

illmillrig/matchTransforms
Code
Issues 0
Pull requests 0
Wiki
Pulse
Graphs
Settings
matchTransforms/matchTransforms.py
6085494 5 hours ago
@illmillrig illmillrig Add files via upload
81 lines (62 sloc) 2.02 KB

def getGlobalTransform(node, tfmPlug="worldMatrix"):
	fn = om.MFnTransform(node)
	plug = fn.findPlug(tfmPlug)

	if plug.isArray():
		plug = plug.elementByLogicalIndex(0)

	mat = plug.asMObject()
	fnMat = om.MFnMatrixData(mat)

	return om.MTransformationMatrix(fnMat.matrix())


def matchTransform(nodes, source, translate=True, rotate=True, scale=True, space=om.MSpace.kWorld, matchPivot=False):
	# confirm/create MSelectionList of nodes

	nodeList = []
	
	if isinstance(nodes, om.MSelectionList):
		dagNode = om.MDagPath()
		for i in xrange(nodes.length()):
			nodes.getDagPath(i, dagNode)
			nodeList.append(dagNode)

	elif isinstance(nodes, om.MObject): or isinstance(nodes, om.MDagPath):
		nodeList.append(om.MDagPath.getAPathTo(nodes))

	elif isinstance(nodes, om.MDagPath):
		nodeList.append(nodes)

	elif isinstance(nodes, om.MDagPathArray):
		for i in xrange(nodes.length()):
			nodeList.append(nodes[i])
		

	# get the proper matrix of source
	if space == om.MSpace.kWorld:
		srcTfm = getGlobalTransform(source, "worldMatrix")
	else:
		srcTfm = getGlobalTransform(source, "matrix")

	# source pos
	pos = srcTfm.getTranslation(space)

	# source pivot
	srcPivot = srcTfm.scalePivot(space)

	# stupid MScriptUtil stuff
	util = om.MScriptUtil()
	util.createFromDouble(0.0, 0.0, 0.0)
	scl = util.asDoublePtr()

	fn = om.MFnTransform()
	for node in nodeList:
	
		if space == om.MSpace.kObject:
			tfm = srcTfm
		else:
			# multiply the global scale and rotation by the nodes parent inverse world matrix to get local rot & scl
			invParent = getGlobalTransform(node, "parentInverseMatrix")
			tfm = om.MTransformationMatrix(srcTfm.asMatrix() * invParent.asMatrix())

		# rotation
		rot = tfm.rotation()

		# scale
		tfm.getScale(scl, space)

		# Set Transforms----------------------------
		fn.setObject(node)
		# set Scaling
		if scale:
			fn.setScale(scl)

		# set Rotation
		if rotate:
			fn.setRotation(rot)

		# set Translation
		if translate:
			if matchPivot:
				nodePivot = fn.scalePivot(space)
				pos += srcPivot - nodePivot

			fn.setTranslation(pos, space)
