
import math
def createExrCamRS( node ):

    mDat = node.metadata()
    reqFields = ['exr/rs/camera/%s' % i for i in ('fov', 'aperture', 'transform')]
    if not set( reqFields ).issubset( mDat ):
        nuke.critical( 'Please select a read node with EXR metadata from RS' )
        return


    first = node.firstFrame()
    last = node.lastFrame()
    ret = nuke.getFramesAndViews( 'Create Camera from Metadata', '%s-%s' %( first, last ) )
    if ret is None:
        return
    fRange = nuke.FrameRange( ret[0] )
     
    cam = nuke.createNode( 'Camera2' )
    cam['useMatrix'].setValue( False )
    
    for k in ('translate', 'rotate'):
        cam[k].setAnimated()
    
    task = nuke.ProgressTask( 'Baking camera from meta data in %s' % node.name() )
    
    for curTask, frame in enumerate( fRange ):
        if task.isCancelled():
            break
        task.setMessage( 'processing frame %s' % frame )
        hap = node.metadata( 'exr/rs/camera/aperture' )[0]
        vap = node.metadata( 'exr/rs/camera/aperture' )[1]
        fov = node.metadata ( 'exr/rs/camera/fov' )
        fstop = node.metadata( 'exr/rs/camera/FStop' )
        fdist = node.metadata( 'exr/rs/camera/DOFFocusDistance' )
        
        focal = float(hap) / ( 2.0 * math.tan( math.radians(fov) * 0.5 ) )

        width = node.metadata( 'input/width', frame )
        height = node.metadata( 'input/height', frame )
        aspect = float(width) / float(height) 
        
        cam['focal'].setValue( float(focal) )
        cam['haperture'].setValue( float(hap) )
        cam['vaperture'].setValue( float(vap) )
        cam['fstop' ].setValue(fstop)
        cam['focal_point' ].setValue(fdist)


        matrixCamera = node.metadata( 'exr/rs/camera/transform', frame ) 
        matrixCreated = nuke.math.Matrix4()
        
        for k,v in enumerate( matrixCamera ):
            matrixCreated[k] = v

        matrixCreated.rotateY( math.radians(-180) ) 
        translate = matrixCreated.transform( nuke.math.Vector3(0,0,0) ) 
        rotate = matrixCreated.rotationsZXY()
    
        cam['translate'].setValueAt( float(translate.x), frame, 0 )
        cam['translate'].setValueAt( float(translate.y), frame, 1 )
        cam['translate'].setValueAt( float(translate.z), frame, 2 )
        cam['rotate'].setValueAt( float( math.degrees( rotate[0] ) ), frame, 0 )
        cam['rotate'].setValueAt( float( math.degrees( rotate[1] ) ), frame, 1 ) 
        cam['rotate'].setValueAt( float( math.degrees( rotate[2] ) ), frame, 2 ) 
    
        task.setProgress( int( float(curTask) / fRange.frames() * 100 ) )

node = None
try:
    node = nuke.selectedNode()
except:
    nuke.critical( 'Please select a read node with EXR metadata from Redshift!' )

if node is not None:
    createExrCamRS( node )