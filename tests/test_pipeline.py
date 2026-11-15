import numpy as np
import pytest
from astropy.table import Table
from astropy.wcs import WCS
from reproject import reproject_interp
from backend.pipeline import Search, selection, download

@pytest.mark.parametrize('kwargs',[{'ra':float('nan'),'dec':0},{'ra':0,'dec':91},{'ra':360,'dec':0},{'ra':0,'dec':0,'fov':100}])
def test_invalid_region(kwargs):
    with pytest.raises(ValueError): Search(**kwargs)

def test_selection_deduplicates_releases_without_merging_detectors():
    rows=Table(rows=[('a','spherex_qr3',1.,'https://irsa.ipac.caltech.edu/ibe/data/spherex/qr3/1/a.fits'),('a','spherex_dr1',1.,'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/1/a.fits'),('b','spherex_dr1',2.,'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/1/b.fits'),('a','spherex_dr1',1.,'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/a.fits')],names=['obs_id','obs_collection','t_min','access_url'])
    result=selection(rows,6)
    assert len(result)==2
    assert result[0]['obs_collection']=='spherex_dr1'
    assert [float(r['t_min']) for r in result]==[1,2]

def test_download_rejects_untrusted_url(tmp_path):
    with pytest.raises(ValueError): download('https://example.com/a.fits',{},tmp_path/'a.fits')

def test_reprojection_known_pixel_shift():
    ref=WCS(naxis=2);ref.wcs.ctype=['RA---TAN','DEC--TAN'];ref.wcs.crval=[10,20];ref.wcs.crpix=[16,16];ref.wcs.cdelt=[-.001,.001]
    shifted=ref.deepcopy();shifted.wcs.crpix=[18,16]
    image=np.zeros((32,32));image[15,17]=1
    result,_=reproject_interp((image,shifted),ref,shape_out=(32,32))
    assert np.unravel_index(np.nanargmax(result),result.shape)==(15,15)
