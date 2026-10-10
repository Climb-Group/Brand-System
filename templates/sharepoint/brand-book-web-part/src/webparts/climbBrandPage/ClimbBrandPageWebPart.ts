import { Version } from '@microsoft/sp-core-library';
import {
  type IPropertyPaneConfiguration,
  PropertyPaneDropdown,
  PropertyPaneTextField
} from '@microsoft/sp-property-pane';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';

import styles from './ClimbBrandPageWebPart.module.scss';
import * as strings from 'ClimbBrandPageWebPartStrings';
import { BRAND_PAGES } from './book/pages';
import { PAGE_PARAM, SLUG, showBookPage } from './book/bookView';

export interface IClimbBrandPageWebPartProps {
  page: string;
  bookUrl: string;
}

export default class ClimbBrandPageWebPart extends BaseClientSideWebPart<IClimbBrandPageWebPartProps> {
  private _shown: string = '';

  public render(): void {
    const base = this._base();
    const slug = this._slug();
    if (this._shown === base + slug) {
      return;
    }
    this._shown = base + slug;
    showBookPage(this.domElement, {
      base,
      slug,
      className: styles.climbBrandPage,
      statusClass: styles.status,
      loading: strings.Loading,
      failed: strings.LoadFailed
    }).then((ok) => {
      if (!ok) {
        this._shown = '';
      }
    }).catch(() => {
      this._shown = '';
    });
  }

  protected get dataVersion(): Version {
    return Version.parse('1.0');
  }

  protected onPropertyPaneFieldChanged(): void {
    this._shown = '';
  }

  protected getPropertyPaneConfiguration(): IPropertyPaneConfiguration {
    return {
      pages: [
        {
          header: { description: strings.PropertyPaneDescription },
          groups: [
            {
              groupName: strings.BasicGroupName,
              groupFields: [
                PropertyPaneDropdown('page', { label: strings.PageFieldLabel, options: BRAND_PAGES }),
                PropertyPaneTextField('bookUrl', {
                  label: strings.BookUrlFieldLabel,
                  description: strings.BookUrlFieldDescription
                })
              ]
            }
          ]
        }
      ]
    };
  }

  // The brand book folder, ending in a slash.
  private _base(): string {
    const set = (this.properties.bookUrl || '').trim();
    const url = set || this.context.pageContext.web.absoluteUrl + '/SiteAssets/BrandCentre/book/';
    return url.charAt(url.length - 1) === '/' ? url : url + '/';
  }

  private _slug(): string {
    const asked = new URLSearchParams(window.location.search).get(PAGE_PARAM) || '';
    if (SLUG.test(asked)) {
      return asked;
    }
    return SLUG.test(this.properties.page || '') ? this.properties.page : 'index';
  }
}
