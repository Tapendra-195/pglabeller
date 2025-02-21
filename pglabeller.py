#!/usr/bin/python3
#
'''
# pglabeller.py
# -- tool to help with photogrammetry image labelling
#
# Authors:  Blair Jamieson
# Date: Jan 2025
# 
# Some notes on the implementation
#
# I decided to use a dictionary called widgetmap to give names to each
# of the widgets, and some special values that I could pass between functions to allow them to be set easier.
# but made it faster to initially write the code
'''

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.font as tkFont

import numpy as np
import sys
from PIL import ImageTk,Image
import PIL
from PIL.ExifTags import TAGS
import datetime as dt 
import threading
import os
import glob

import argparse
import cv2 as cv

# globals
zoomimgsize = 450 # number of pixels x and y for a zoom image
fontsize = 12

style = None

blob_params = cv.SimpleBlobDetector_Params()
blob_params.blobColor = 255
blob_params.minThreshold = 5
blob_params.maxThreshold = 255
blob_params.filterByArea = True
blob_params.minArea = 30
blob_params.maxArea = 9999999
blob_params.minDistBetweenBlobs = 100
blob_params.filterByCircularity = False
blob_params.filterByColor = False
blob_params.filterByInertia = False

current_keypoints = []

class CameraSetting:
    def __init__(self, lastimg='c1.jpg'):
        self.get_camera_settings( lastimg )

    def get_camno_from_filename( self, imgname ):
        path_file = os.path.split( imgname )
        return int( path_file[1][1] )
        
    def get_camera_settings(self, lastimg='c1.jpg' ):
        '''
        This function should get the current camera settings.
        For now it just sets arbitrary values
        
        Parameters
        ----------
        lastimg : JPG image filename 'cN*.jpg' -- where N is camera number! 
        
        Returns
        -------
        None.

        '''
        # current camera settings for next photo
        self.camno = self.get_camno_from_filename( lastimg )
        
        # settings of last photo
        self.lastimage = lastimg
        self.get_image_data( lastimg )
        
    def load_new_last_image(self, lastimg):
        del self.pil_image
        self.get_camera_settings(lastimg)
        
    def get_image_data(self, lastimg):
        create_time = os.path.getctime( lastimg )
        self.file_create_date = dt.datetime.fromtimestamp(create_time)
        self.pil_image = PIL.Image.open( lastimg )
        # extract EXIF data
        exifdata = self.pil_image._getexif()
        exifdict = dict ( (TAGS.get(k,k),v) for k,v in exifdata.items() if sys.getsizeof(k)<100 and sys.getsizeof(v)<500)
     
        self.image_digitized_date = exifdict['DateTimeDigitized']
        self.image_iso = exifdict['ISOSpeedRatings']
        self.image_ss = str( exifdict['ExposureTime'] ) 
        self.image_width = int( exifdict['ExifImageWidth'] )
        self.image_height = int( exifdict['ExifImageHeight'] )
            

camera_settings = None
        
def update_datetime_widget( win, lbl ):
    '''
    
    Parameters
    ----------
    win : tk.Frame holding the label
    lbl : ttk.Label
        Label to be updated with current date and time every 2 sec

    Returns
    ------- 
    None.

    '''
    date = dt.datetime.now()
    lbl.config( text = date.strftime("%B %d, %Y  %I:%M%p")+'  --  PGGUI Camera Control  --  Author: Blair Jamieson (Jan. 2025)', anchor='center' )
    win.update()
    lbl.after(60000, lambda: update_datetime_widget(win, lbl))

def draw_blobs_on_images( win, widgetmap ):
    global camera_settings
    global current_keypoints
    
    camset = camera_settings
 
    origsize = camset.pil_image.size
    imgscalefactor = 1024/  float(origsize[0])
    print('Image scale factor = ',imgscalefactor)
    imgheight = int( imgscalefactor*origsize[1] )
    
    zxmin, zymin = widgetmap['imgzoom_xymin']
    zxmin -= 34
    zymin -= 19

    print('zxmin,zymin=',zxmin,zymin)
    print('imgzoom_xymin=',widgetmap['imgzoom_xymin'])
    
    for i,kp in enumerate(current_keypoints):
        print( 'x,y,r=',kp.pt[0],kp.pt[1],kp.size)
        x = kp.pt[0]
        y = kp.pt[1]
        r = kp.size / 2
        xsc = int( x*imgscalefactor )
        ysc = int( y*imgscalefactor )
        rsc = int( r*imgscalefactor )
        canvas_img_ova = widgetmap[ 'canvas_img' ].create_oval( ( (xsc-rsc,ysc-rsc),(xsc+rsc,ysc+rsc) ), outline='red')
        #widgetmap['canvas_img_ova_'+str(i) ] = canvas_img_ova
        if x>zxmin and y>zymin and x<zxmin+zoomimgsize and y<zymin+zoomimgsize:
            xoffs = x-zxmin
            yoffs = y-zymin
            print('xoffs,yoffs=',xoffs,yoffs)
            canvas_img_oval = widgetmap[ 'canvas_imgzoom' ].create_oval( ( (xoffs-r,yoffs-r), (xoffs+r,yoffs+r) ), outline='red' )
            #widgetmap['canvas_img_oval_'+str(i)] = canvas_img_oval
    

class xypoint:
    def __init__(self,xx=0,yy=0):
        self.x = xx
        self.y = yy

def detect_blobs( win, widgetmap ):
    global current_keypoints
    global camera_setting

    widgetmap[ 'lbl_status']['text'] = 'BUSY'
    widgetmap[ 'lbl_status']['style'] ='Red.TLabel'
    win.update()

    blob_params.blobColor = int( float(widgetmap['entry_blobcolor'].get()) )
    blob_params.minThreshold = int( float(widgetmap['entry_minThres'].get()) )
    blob_params.maxThreshold = int( float(widgetmap['entry_maxThres'].get()) )
    blob_params.minArea = int( float(widgetmap['entry_minArea'].get()) )
    blob_params.minDistBetweenBlobs = int( float(widgetmap['entry_minDist'].get()) )

    bdetector = cv.SimpleBlobDetector_create( blob_params )

    img = cv.imread( camera_settings.lastimage , cv.IMREAD_GRAYSCALE)    

    bilateral = cv.bilateralFilter(img, 15, 125, 125)

    current_keypoints = bdetector.detect( bilateral )

    widgetmap[ 'lbl_numBlobs' ]['text'] = 'Number of blobs: '+ str( len(current_keypoints) )

    xy = xypoint( widgetmap['xymin'][0], widgetmap['xymin'][1] )
    on_image_click( win, xy, camera_settings, widgetmap, widgetmap['imgscalefactor'])
    #draw_blobs_on_images( win, widgetmap )
    
    widgetmap[ 'lbl_status']['text'] = 'READY'
    widgetmap[ 'lbl_status']['style'] ='Green.TLabel'
    win.update()

    
    
def select_input_file( win, widgetmap ):
    global camera_settings
    widgetmap['var_inputfile'].set( tk.filedialog.askopenfilename(initialdir='./',title='Select JPG file', filetypes=[('Images', '*.jpg *.JPG *.jpeg')] ) )
    camera_settings = CameraSetting( str( widgetmap['var_inputfile'].get() ) )
    setup_new_imagefile( win, widgetmap )


def setup_new_imagefile( win, widgetmap ):
    global camera_settings
    widgetmap[ 'lbl_status']['text'] = 'BUSY'
    widgetmap[ 'lbl_status']['style'] ='Red.TLabel'
    win.update()
    
 
    camset = camera_settings

    origsize = camset.pil_image.size
    imgscalefactor = 1024/  float(origsize[0])
    print('Image scale factor = ',imgscalefactor)
    imgheight = int( imgscalefactor*origsize[1] )
    widgetmap['imgscalefactor'] = imgscalefactor

    # cleanup old zoomcanvas
    widgetmap['canvas_imgzoom'].delete('all')
    # add new image to canvas
    crop_rectangle = (0.,0.,zoomimgsize,zoomimgsize)
    crop_img = camset.pil_image.crop( crop_rectangle )
    tkcropimg = PIL.ImageTk.PhotoImage(crop_img)
    widgetmap['canvas_imgzoom'].create_text( 0., 0., text='0, 0',anchor='nw', fill='red')
    new_canvas_imgzoom_id = widgetmap['canvas_imgzoom'].create_image( 35, 20, image=tkcropimg,anchor='nw')
    widgetmap['canvas_imgzoom'].create_text( 500, 500, text='450, 450',anchor='se', fill='red')
    del widgetmap['cropimg'] #cleanup old cropimg
    widgetmap['cropimg'] = tkcropimg
    widgetmap['imgzoom_xymin'] = [0,0]
    
    widgetmap['canvas_imgzoom'].tag_bind( new_canvas_imgzoom_id, '<Enter>', lambda ev : on_imagezoom_enter(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_imgzoom'].tag_bind( new_canvas_imgzoom_id, '<Leave>', lambda ev : on_imagezoom_leave(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_imgzoom'].tag_bind( new_canvas_imgzoom_id, '<Motion>', lambda ev : on_imagezoom_motion(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_imgzoom_id'] = new_canvas_imgzoom_id
    # cleanup old canvas

    widgetmap[ 'lbl_imgzoom_xy' ]['text']  = "x = 0, y = 0" 
      
    widgetmap[ 'canvas_img'].delete('all')
    pilimg = camset.pil_image.resize( (1024,  imgheight), PIL.Image.LANCZOS )
    tkimg = PIL.ImageTk.PhotoImage( pilimg )
    new_canvas_img_id = widgetmap[ 'canvas_img'].create_image( 1024, imgheight, image = tkimg, anchor='se' )
    recmax = int( 450*imgscalefactor )
    canvas_rec_id = widgetmap[ 'canvas_img' ].create_rectangle( 1,1,recmax+1,recmax+1, outline='red')
    widgetmap['canvas_rec_id'] = canvas_rec_id
     
    widgetmap['canvas_img'].tag_bind( new_canvas_img_id, '<Button-1>', lambda ev : on_image_click( win, ev, camset, widgetmap, imgscalefactor) )
    widgetmap['canvas_img'].tag_bind( new_canvas_img_id, '<Enter>', lambda ev : on_image_enter(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_img'].tag_bind( new_canvas_img_id, '<Leave>', lambda ev : on_image_leave(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_img'].tag_bind( new_canvas_img_id, '<Motion>', lambda ev : on_image_motion(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_img_id'] = new_canvas_img_id
    
    del widgetmap['curimg'] # delete old rescaled image  
    widgetmap['curimg'] = tkimg
    
    # update text under image
    widgetmap[ 'lbl_img_xy' ]['text'] = 'x = 0, y = 0'

    widgetmap[ 'lbl_img_file' ]['text'] = 'Filename: '+str(camset.lastimage)
    widgetmap[ 'lbl_img_filedate' ]['text'] = 'File creation date: '+str(camset.file_create_date)
    widgetmap[ 'lbl_img_digidate' ]['text'] = 'Image digitization date: '+str(camset.image_digitized_date)
    widgetmap[ 'lbl_img_iso' ]['text']  = 'ISO: '+str(camset.image_iso)
    widgetmap[ 'lbl_img_ss' ]['text']  = 'Shutterspeed: '+str(camset.image_ss)
    widgetmap[ 'lbl_img_size' ]  = 'Size: '+str(camset.image_width)+'x'+str(camset.image_height)
   
    #update_camera_readback_values( widgetmap, camset )
    widgetmap[ 'lbl_status']['text'] = 'Ready'
    widgetmap[ 'lbl_status']['style'] ='Green.TLabel'
    win.update()


                                    
def setup_image_widgets( win, image_filename ):
    '''
    This sets up the vast majority of the widgets in some initial state.
    
    Parameters
    ----------
    win : TYPE tk.Frame
        Adds widgets to display camera settings
    image_filename : TYPE str
        Filename of image to label
    Returns
    -------
    dictionary of setting name : pointer to widget

    '''
    global camera_settings
    camera_settings = CameraSetting( image_filename )                                    
                                    
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=fontsize)
    
    
    widgetmap = {}
    
    # Put date in a frame of its own at top
    top_frame = tk.Frame(win, width=1200, height=40, bg='skyblue')
    top_frame.pack(side='top', fill='both', padx=10, pady=5, expand=True)
    
    widgetmap[ 'lbl_date' ] = ttk.Label( top_frame, text='todays date' )
    widgetmap[ 'lbl_date' ].pack(side='top', fill='both', padx=20, pady=5)    
    update_datetime_widget(top_frame, widgetmap['lbl_date'])

    widgetmap[ 'lbl_lblinputfile' ]  = ttk.Label( top_frame, text="Input file:" )
    widgetmap[ 'lbl_lblinputfile' ].pack(side=tk.LEFT,padx=10)
    widgetmap[ 'var_inputfile'] = tk.StringVar()
    widgetmap[ 'var_inputfile'].set(image_filename)
    widgetmap[ 'lbl_inputfile' ] = ttk.Label( top_frame, textvariable=widgetmap['var_inputfile'] )
    widgetmap[ 'lbl_inputfile' ].pack(side=tk.LEFT,padx=10)
 
    widgetmap[ 'btn_inputfile' ] = ttk.Button( top_frame, text = "Select input", command = lambda: select_input_file( win , widgetmap ) )
    widgetmap[ 'btn_inputfile'].pack(side=tk.LEFT,padx=10)

     
    mid_frame= tk.Frame(win,width=1200,height=800, bg='grey')
    mid_frame.pack(side='top', fill='both', padx=10, pady=5, expand=True)
    
    left_frame = tk.Frame(mid_frame, width=400, height=400, bg='skyblue')
    left_frame.pack( side='left', fill='both', padx=10, pady=5, expand=True)

    blob_frame = tk.Frame(left_frame, width=380, height=40 )
    blob_frame.pack(side='top', fill='both', padx=5, pady =5)
    
    widgetmap[ 'lbl_blobcolor'] = ttk.Label( blob_frame, text='blobColor [0-255]' )
    widgetmap[ 'lbl_blobcolor'].pack(side=tk.LEFT,padx=10)
    widgetmap[ 'entry_blobcolor' ] = ttk.Entry( blob_frame, width=5 )
    widgetmap[ 'entry_blobcolor' ].insert( 0, int(blob_params.blobColor) )
    widgetmap[ 'entry_blobcolor' ].pack(side=tk.LEFT,padx=10)

    widgetmap[ 'lbl_status'] = ttk.Label( blob_frame, text='Ready', style='Green.TLabel')
    widgetmap[ 'lbl_status'].pack(side=tk.RIGHT,padx=10)

    blobmint_frame = tk.Frame(left_frame, width=380, height=40 )
    blobmint_frame.pack(side='top', fill='both', padx=5, pady =5)
    widgetmap[ 'lbl_minThres'] = ttk.Label( blobmint_frame, text='blob minThres [0-255]' )
    widgetmap[ 'lbl_minThres'].pack(side=tk.LEFT,padx=10)
    widgetmap[ 'entry_minThres' ] = ttk.Entry( blobmint_frame, width=5 )
    widgetmap[ 'entry_minThres' ].insert( 0, int(blob_params.minThreshold) )
    widgetmap[ 'entry_minThres' ].pack(side=tk.LEFT,padx=10)
                                    
    #blobmaxt_frame = tk.Frame(left_frame, width=380, height=40 )
    #blobmaxt_frame.pack(side='top', fill='both', padx=5, pady =5)
    widgetmap[ 'lbl_maxThres' ] = ttk.Label( blobmint_frame, text='blob maxThres [0-255]' )
    widgetmap[ 'lbl_maxThres'].pack(side=tk.LEFT,padx=10)
    widgetmap[ 'entry_maxThres' ] = ttk.Entry( blobmint_frame, width=5 )
    widgetmap[ 'entry_maxThres' ].insert( 0, int(blob_params.maxThreshold) )
    widgetmap[ 'entry_maxThres' ].pack(side=tk.LEFT,padx=10)
                                
    blobmina_frame = tk.Frame(left_frame, width=380, height=40 )
    blobmina_frame.pack(side='top', fill='both', padx=5, pady =5)
    widgetmap[ 'lbl_minArea' ] = ttk.Label( blobmina_frame, text='blob minArea' )
    widgetmap[ 'lbl_minArea'].pack(side=tk.LEFT,padx=10)
    widgetmap[ 'entry_minArea' ] = ttk.Entry( blobmina_frame, width=5 )
    widgetmap[ 'entry_minArea' ].insert( 0, int(blob_params.minArea) )
    widgetmap[ 'entry_minArea' ].pack(side=tk.LEFT,padx=10)

    #blobmindis_frame = tk.Frame(left_frame, width=380, height=40 )
    #blobmindis_frame.pack(side='top', fill='both', padx=5, pady =5)
    widgetmap[ 'lbl_minDist' ] = ttk.Label( blobmina_frame, text='blob dist between' )
    widgetmap[ 'lbl_minDist'].pack(side=tk.LEFT,padx=10)
    widgetmap[ 'entry_minDist' ] = ttk.Entry( blobmina_frame, width=5 )
    widgetmap[ 'entry_minDist' ].insert( 0, int(blob_params.minDistBetweenBlobs) )
    widgetmap[ 'entry_minDist' ].pack(side=tk.LEFT,padx=10)

    
    blobbtn_frame = tk.Frame(left_frame, width=380, height=40 )
    blobbtn_frame.pack(side='top', fill='both', padx=5, pady =5)

    widgetmap[ 'btn_blobdetect' ] = ttk.Button( blobbtn_frame, text = "Detect blobs", command = lambda: detect_blobs( win, widgetmap ) )
    widgetmap[ 'btn_blobdetect'].pack(side=tk.LEFT)

                            
    widgetmap[ 'lbl_numBlobs' ] = ttk.Label( blobbtn_frame, text='Number of blobs: 0' )
    widgetmap[ 'lbl_numBlobs'].pack(side=tk.LEFT,padx=10)
                                    
    
    
 
    origsize = camera_settings.pil_image.size
    imgscalefactor = 1024/  float(origsize[0])
    print('Image scale factor = ',imgscalefactor)
    imgheight = int( imgscalefactor*origsize[1] )
    
    widgetmap['canvas_imgzoom'] = tk.Canvas(left_frame, width=500, height=500)
    widgetmap['canvas_imgzoom'].pack(fill='both', padx=10,pady=10,expand=True)
    widgetmap['xymin'] = [0,0]
    crop_rectangle = (0.,0.,zoomimgsize,zoomimgsize)
    crop_img = camera_settings.pil_image.crop( crop_rectangle )
    tkcropimg = PIL.ImageTk.PhotoImage(crop_img)
    widgetmap['canvas_imgzoom'].create_text( 0., 0., text='0, 0',anchor='nw', fill='red')
    canvas_imgzoom_id = widgetmap['canvas_imgzoom'].create_image( 35, 20, image=tkcropimg,anchor='nw')
    widgetmap['canvas_imgzoom_id'] = canvas_imgzoom_id
    widgetmap['canvas_imgzoom'].create_text( 500, 500, text='450, 450',anchor='se', fill='red')
    widgetmap['cropimg'] = tkcropimg
    widgetmap['imgzoom_xymin'] = [0,0]
    widgetmap['canvas_imgzoom'].tag_bind( canvas_imgzoom_id, '<Enter>', lambda ev : on_imagezoom_enter(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_imgzoom'].tag_bind( canvas_imgzoom_id, '<Leave>', lambda ev : on_imagezoom_leave(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_imgzoom'].tag_bind( canvas_imgzoom_id, '<Motion>', lambda ev : on_imagezoom_motion(ev,widgetmap,imgscalefactor) )
 
    widgetmap[ 'lbl_imgzoom_xy' ]  = ttk.Label( left_frame, text="x = 0, y = 0" )
    widgetmap[ 'lbl_imgzoom_xy' ].pack(side=tk.TOP,fill='both',padx=10,expand=True)
  
    right_frame = tk.Frame(mid_frame, width=1044, height=imgheight+10, bg='lightgrey')
    right_frame.pack( side='right', fill='both', padx=10, pady=5, expand=True)
    
    widgetmap[ 'canvas_img'] = tk.Canvas( right_frame, width=1024, height=imgheight )
    widgetmap[ 'canvas_img'].pack()
    print('set image:',camera_settings.lastimage)
    pilimg = camera_settings.pil_image.resize( (1024,  imgheight), PIL.Image.LANCZOS )
    tkimg = PIL.ImageTk.PhotoImage( pilimg )
    canvas_img_id = widgetmap[ 'canvas_img'].create_image( 1024, imgheight, image = tkimg, anchor='se' )
    widgetmap['canvas_img_id'] = canvas_img_id
    recmax = int( 450*imgscalefactor )
    canvas_rec_id = widgetmap[ 'canvas_img' ].create_rectangle( 1,1,recmax+1,recmax+1, outline='red')
    widgetmap['canvas_rec_id'] = canvas_rec_id
    widgetmap['canvas_img'].tag_bind( canvas_img_id, '<Button-1>', lambda ev : on_image_click(win, ev, camera_settings, widgetmap, imgscalefactor) )
    widgetmap['canvas_img'].tag_bind( canvas_img_id, '<Enter>', lambda ev : on_image_enter(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_img'].tag_bind( canvas_img_id, '<Leave>', lambda ev : on_image_leave(ev,widgetmap,imgscalefactor) )
    widgetmap['canvas_img'].tag_bind( canvas_img_id, '<Motion>', lambda ev : on_image_motion(ev,widgetmap,imgscalefactor) )
    
    
    widgetmap['curimg'] = tkimg

    
    widgetmap[ 'lbl_img_xy' ]  = ttk.Label( right_frame, text="x = 0, y = 0" )
    widgetmap[ 'lbl_img_xy' ].pack(side=tk.TOP,padx=10)

    widgetmap[ 'lbl_img_file' ]  = ttk.Label( right_frame, text="Filename: "+str(camera_settings.lastimage))
    widgetmap[ 'lbl_img_file' ].pack(side=tk.TOP,padx=10)
    
    widgetmap[ 'lbl_img_filedate' ]  = ttk.Label( right_frame, text="File creation date: "+str(camera_settings.file_create_date))
    widgetmap[ 'lbl_img_filedate' ].pack(side=tk.TOP,padx=10)
  
    widgetmap[ 'lbl_img_digidate' ]  = ttk.Label( right_frame, text="Image digitization date: "+str(camera_settings.image_digitized_date))
    widgetmap[ 'lbl_img_digidate' ].pack(side=tk.TOP,padx=10)
    
    widgetmap[ 'lbl_img_iso' ]  = ttk.Label( right_frame, text="ISO: "+str(camera_settings.image_iso))
    widgetmap[ 'lbl_img_iso' ].pack(side=tk.TOP,padx=10)
    
    widgetmap[ 'lbl_img_ss' ]  = ttk.Label( right_frame, text="Shutterspeed: "+str(camera_settings.image_ss))
    widgetmap[ 'lbl_img_ss' ].pack(side=tk.TOP,padx=10)
    
    widgetmap[ 'lbl_img_size' ]  = ttk.Label( right_frame, text="Size: "+str(camera_settings.image_width)+'x'+str(camera_settings.image_height))
    widgetmap[ 'lbl_img_size' ].pack(side=tk.TOP,padx=10)
 
    widgetmap[ 'canvas_status'] = tk.Canvas( right_frame, width=1025, height=50 )
    widgetmap[ 'canvas_status'].pack()
 
    return widgetmap


def on_imagezoom_enter(ev,widgetmap,imgscalefactor):
    offsetx, offsety = widgetmap['imgzoom_xymin']
    offsetx -= 34
    offsety -= 19
    widgetmap[ 'canvas_imgzoom'].config( cursor='cross')
    widgetmap['lbl_imgzoom_xy']['text'] = 'x = '+str( offsetx+int(ev.x) )+', y = '+str( offsety+int(ev.y) )
    

def on_imagezoom_leave(ev,widgetmap,imgscalefactor):
    widgetmap[ 'canvas_imgzoom'].config( cursor='arrow')
    

def on_imagezoom_motion(ev,widgetmap,imgscalefactor):
    offsetx, offsety = widgetmap['imgzoom_xymin']
    offsetx -= 34
    offsety -= 19
    widgetmap['lbl_imgzoom_xy']['text'] = 'x = '+str( offsetx+int(ev.x) )+', y = '+str( offsety+int(ev.y) )


def on_image_enter(ev, widgetmap, imgscale):
    widgetmap[ 'canvas_img'].config( cursor='cross')
    widgetmap['lbl_img_xy']['text'] = 'x = '+str( int(ev.x/imgscale) )+', y = '+str( int(ev.y/imgscale) )
    
    
def on_image_leave(ev, widgetmap, imgscale):
    widgetmap[ 'canvas_img'].config( cursor='arrow')
    
def on_image_motion(ev, widgetmap, imgscale):
    widgetmap['lbl_img_xy']['text'] = 'x = '+str( int(ev.x/imgscale) )+', y = '+str( int(ev.y/imgscale) )
        

def on_image_click( win, xy, camset, widgetmap, imgscale):
    widgetmap[ 'lbl_status']['text'] = 'BUSY'
    win.update()
    x,y = xy.x, xy.y
    xfull = int( x/imgscale )
    yfull = int( y/imgscale )

    if xfull + zoomimgsize > camset.image_width:
        xfull = camset.image_width-zoomimgsize
    if yfull + zoomimgsize > camset.image_height:
        yfull = camset.image_height-zoomimgsize

    widgetmap['xymin'] = [x,y]
    widgetmap['imgzoom_xymin'] = [xfull,yfull]
    x = int(xfull*imgscale)
    y = int(yfull*imgscale)
    widgetmap['canvas_img'].delete( widgetmap['canvas_rec_id'] )
    
    recmaxxy = int( x+zoomimgsize*imgscale ), int( y+zoomimgsize*imgscale )
    widgetmap['canvas_rec_id'] = widgetmap[ 'canvas_img' ].create_rectangle( x, y,recmaxxy[0],recmaxxy[1], outline='red')

    widgetmap['canvas_imgzoom'].delete('all')
    crop_rectangle = ( xfull, yfull, xfull+zoomimgsize, yfull+zoomimgsize)
    crop_img = camset.pil_image.crop( crop_rectangle )
    tkcropimg = PIL.ImageTk.PhotoImage(crop_img)
    widgetmap['canvas_imgzoom'].create_text( 0., 0., text=str(xfull)+', '+str(yfull),anchor='nw', fill='red')
    canvas_imgzoom_id = widgetmap['canvas_imgzoom'].create_image( 35, 20, image=tkcropimg,anchor='nw')
    widgetmap['canvas_imgzoom'].create_text( 500, 500, text=str(xfull+zoomimgsize)+', '+str(yfull+zoomimgsize),anchor='se', fill='red')
    widgetmap['cropimg'] = tkcropimg

    widgetmap['canvas_imgzoom'].tag_bind( canvas_imgzoom_id, '<Enter>', lambda ev : on_imagezoom_enter(ev,widgetmap,imgscale) )
    widgetmap['canvas_imgzoom'].tag_bind( canvas_imgzoom_id, '<Leave>', lambda ev : on_imagezoom_leave(ev,widgetmap,imgscale) )
    widgetmap['canvas_imgzoom'].tag_bind( canvas_imgzoom_id, '<Motion>', lambda ev : on_imagezoom_motion(ev,widgetmap,imgscale) )

    draw_blobs_on_images( win, widgetmap )   
   
    widgetmap[ 'lbl_status']['text'] = 'Ready'
    widgetmap[ 'lbl_status']['style'] ='Green.TLabel'
    win.update()


class CameraControlWindow( tk.Tk ):
    """
    Main tkinter window for the Camera Control GUI
    """
    
    def __init__( self, *args, **kwargs ):
        """
        Initialize the window
        """
        tk.Tk.__init__( self, *args, **kwargs )
        tk.Tk.wm_title( self, "pglabeller image labeller" )

        self.main_window = tk.Frame( self )
        self.main_window.pack(side="top", fill="both", expand = True )
        self.main_window.grid_rowconfigure(0, weight=1)
        self.main_window.grid_columnconfigure(0, weight=1)

        global style
        style=ttk.Style()
        style.configure("Red.TLabel", foreground="red")
        style.configure("Green.TLabel", foreground="green")

        parser = argparse.ArgumentParser(description='pglabeller command line options')
        parser.add_argument('--img',default='/home/jamieson/pgdata/ALLon/c1_img20241130-14:22:36CET.jpg',help='image to label',type=str )

        argsparsed = parser.parse_args()
        print(argsparsed)


        self.camset_widgets = setup_image_widgets( self.main_window, argsparsed.img )


        # quit button
        bottom_frame = tk.Frame(self.main_window, width=1200, height=40, bg='skyblue')
        bottom_frame.pack( side='top', fill='both', padx=10, pady=5, expand=True)
        
        self.camset_widgets[ 'btn_quit']  = ttk.Button( bottom_frame, text = "Quit", command = lambda: self.quit() )
        self.camset_widgets[ 'btn_quit'].pack(side='bottom',fill="both",expand=True)
            

    def quit( self ):
        """
        Quit program. Couldn't get it to cleanup properly, so just did kludge sys.exit()
        """
        self.main_window.destroy()
        self.destroy()
        print("Goodbye.")
        sys.exit()




if __name__ == '__main__':

    root = tk.Tk()

    root.destroy()

    app = CameraControlWindow( )
    app.mainloop()

